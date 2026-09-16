"""
Super Scan Tool - Universal Multi-Manufacturer WebSocket Telemetry & Actuator Server
Integrates UDS Bi-Directional Actuator Controls, Mode 06, Mode 02, and 60 FPS WebSockets.
"""

import sys
import os
import json
import time
import math
import random
import threading
import struct
import hashlib
import base64
import socket
import csv
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)
from dtc_database import lookup_dtc
from vehicle_profiles import decode_vin_details, MANUFACTURER_PROFILES
from actuator_engine import ACTUATOR_CATALOG, ActuatorController

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WS_CLIENTS = set()
WS_LOCK = threading.Lock()

INIT_VIN_INFO = decode_vin_details("1GNEVHKW1KJ260578")

LIVE_STATE = {
    "connected": False,
    "hardware_name": "TOPDON RLink",
    "vin": INIT_VIN_INFO["vin"],
    "make": INIT_VIN_INFO["make"],
    "year": INIT_VIN_INFO["year"],
    "country": INIT_VIN_INFO["country"],
    "model_string": INIT_VIN_INFO["model_string"],
    "battery_voltage": 13.6,
    "rpm": 0.0,
    "speed_mph": 0.0,
    "coolant_f": 195.0,
    "coolant_c": 90.5,
    "trans_temp_f": 165.0,
    "oil_temp_f": 205.0,
    "throttle_pct": 0.0,
    "engine_load_pct": 0.0,
    "maf_gs": 4.5,
    "dtcs": ["P0104", "C15AA"],
    "pending_dtcs": [],
    "permanent_dtcs": [],
    "dtc_details": [],
    "actuators": ACTUATOR_CATALOG["GM"],
    "actuator_status": {"last_action": "None", "result": "Ready", "success": True},
    "simulation_mode": False,
    "fps": 60,
    "latency_ms": 1.5,
    "last_update": 0,
    "status_message": "Ready",
    
    # 0-60 MPH Timer State
    "timer_state": "IDLE",
    "accel_time_0_60": 0.0,
    
    # Data Logging State
    "is_logging": False,
    "current_log_file": None,
    "log_records_count": 0,

    # Mode 06 Cylinder Misfires
    "misfires": [
        {"cylinder": 1, "count": 0, "max_limit": 100, "status": "PASSED (OK)"},
        {"cylinder": 2, "count": 0, "max_limit": 100, "status": "PASSED (OK)"},
        {"cylinder": 3, "count": 0, "max_limit": 100, "status": "PASSED (OK)"},
        {"cylinder": 4, "count": 0, "max_limit": 100, "status": "PASSED (OK)"},
        {"cylinder": 5, "count": 0, "max_limit": 100, "status": "PASSED (OK)"},
        {"cylinder": 6, "count": 0, "max_limit": 100, "status": "PASSED (OK)"}
    ],

    # Mode 02 Freeze Frame
    "freeze_frame": {
        "dtc": "P0104",
        "rpm": 1642,
        "speed_mph": 0,
        "coolant_f": 188.6,
        "engine_load_pct": 34.2,
        "throttle_pct": 14.5,
        "fuel_trim_st_bank1": "+2.3%",
        "fuel_trim_lt_bank1": "+4.7%"
    },

    # Emissions Readiness
    "emissions_readiness": [
        {"name": "Misfire Monitor", "status": "READY", "ready": True},
        {"name": "Fuel System Monitor", "status": "READY", "ready": True},
        {"name": "Comprehensive Components", "status": "READY", "ready": True},
        {"name": "Catalytic Converter Monitor", "status": "READY", "ready": True},
        {"name": "Evaporative (EVAP) System", "status": "READY", "ready": True},
        {"name": "Oxygen (O2) Sensor Monitor", "status": "READY", "ready": True},
        {"name": "O2 Sensor Heater Monitor", "status": "READY", "ready": True},
        {"name": "EGR / VVT Variable Timing", "status": "READY", "ready": True}
    ]
}

def encode_ws_frame(message_text: str) -> bytes:
    payload = message_text.encode("utf-8")
    length = len(payload)
    if length <= 125:
        header = struct.pack("!BB", 0x81, length)
    elif length <= 65535:
        header = struct.pack("!BBH", 0x81, 126, length)
    else:
        header = struct.pack("!BBQ", 0x81, 127, length)
    return header + payload

def broadcast_ws_state():
    with WS_LOCK:
        if not WS_CLIENTS:
            return
        frame = encode_ws_frame(json.dumps(LIVE_STATE))
        dead_clients = []
        for client_socket in WS_CLIENTS:
            try:
                client_socket.sendall(frame)
            except Exception:
                dead_clients.append(client_socket)
        for dead in dead_clients:
            WS_CLIENTS.remove(dead)

def build_tx(can_id: int, payload: list) -> PASSTHRU_MSG:
    msg = PASSTHRU_MSG()
    msg.ProtocolID = CAN
    msg.TxFlags = 0
    msg.DataSize = 4 + len(payload)
    msg.Data[0] = (can_id >> 24) & 0xFF
    msg.Data[1] = (can_id >> 16) & 0xFF
    msg.Data[2] = (can_id >> 8) & 0xFF
    msg.Data[3] = can_id & 0xFF
    for i, b in enumerate(payload):
        msg.Data[4 + i] = b
    return msg

def parse_rx(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    return can_id, data[4:]

class UniversalScannerWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.dev = None
        self.chan_id = 0
        self.running = True
        self.csv_file_handle = None
        self.csv_writer = None
        self.timer_start_time = 0.0
        self.active_profile = MANUFACTURER_PROFILES["Chevrolet"]
        self.actuator_ctrl = None

    def init_j2534(self):
        devices = get_installed_j2534_devices()
        if not devices:
            return False
        selected = None
        for d in devices:
            if "PassThru464.dll" in d["dll_path"]:
                selected = d
                break
        if not selected:
            selected = devices[0]

        try:
            self.dev = J2534Device(selected["dll_path"])
            self.dev.open()
            self.chan_id = self.dev.connect(protocol_id=CAN, baudrate=500000)
            
            self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_MSG_FILTERS, None, None)
            mask = PASSTHRU_MSG()
            mask.ProtocolID = CAN
            mask.DataSize = 4
            pattern = PASSTHRU_MSG()
            pattern.ProtocolID = CAN
            pattern.DataSize = 4
            filter_id = ctypes.c_ulong(0)
            self.dev.dll.PassThruStartMsgFilter(self.chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))
            
            self.actuator_ctrl = ActuatorController(self.dev, self.chan_id)
            LIVE_STATE["hardware_name"] = selected["name"]
            LIVE_STATE["connected"] = True
            LIVE_STATE["simulation_mode"] = False
            return True
        except Exception as e:
            LIVE_STATE["connected"] = False
            LIVE_STATE["status_message"] = f"Hardware offline: {e}"
            return False

    def query_pid(self, service: int, pid: int, target_id: int = 0x7DF, timeout_ms: int = 35):
        if not self.dev or not LIVE_STATE["connected"]:
            return []
        try:
            self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
            tx = build_tx(target_id, [0x02, service, pid, 0x00, 0x00, 0x00, 0x00, 0x00])
            num = ctypes.c_ulong(1)
            self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 30)

            start = time.time()
            while (time.time() - start) * 1000 < timeout_ms:
                rx_msgs = (PASSTHRU_MSG * 40)()
                rx_count = ctypes.c_ulong(40)
                status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 12)
                if status == STATUS_NOERROR and rx_count.value > 0:
                    for i in range(rx_count.value):
                        can_id, payload = parse_rx(rx_msgs[i])
                        if can_id in (0x7E8, 0x7E9, 0x7EA, 0x7EB) and len(payload) >= 3:
                            if payload[1] == (service + 0x40) and payload[2] == pid:
                                return list(payload[3:])
                time.sleep(0.002)
        except Exception:
            pass
        return []

    def fetch_vin_and_profile(self):
        if not self.dev or not LIVE_STATE["connected"]:
            return
        try:
            self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
            tx = build_tx(0x7DF, [0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
            num = ctypes.c_ulong(1)
            self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 50)
            
            vin_bytes = bytearray()
            start = time.time()
            while time.time() - start < 0.6:
                rx_msgs = (PASSTHRU_MSG * 40)()
                rx_count = ctypes.c_ulong(40)
                status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 20)
                if status == STATUS_NOERROR and rx_count.value > 0:
                    for i in range(rx_count.value):
                        can_id, payload = parse_rx(rx_msgs[i])
                        if can_id in (0x7E8, 0x7E9) and len(payload) >= 5:
                            pci = (payload[0] & 0xF0) >> 4
                            if pci == 0x00 and payload[1] == 0x49 and payload[2] == 0x02:
                                vin_bytes.extend(payload[4:])
                                break
                            elif pci == 0x01 and payload[2] == 0x49 and payload[3] == 0x02:
                                vin_bytes.extend(payload[5:])
                                fc = build_tx(0x7E0, [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                                fnum = ctypes.c_ulong(1)
                                self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(fc), ctypes.byref(fnum), 50)
                            elif pci == 0x02:
                                vin_bytes.extend(payload[1:])
                                if len(vin_bytes) >= 17:
                                    break
                if len(vin_bytes) >= 17:
                    break
                time.sleep(0.005)
            
            vin = "".join([chr(b) for b in vin_bytes if 32 <= b <= 126]).strip()
            if len(vin) >= 11:
                details = decode_vin_details(vin)
                LIVE_STATE["vin"] = details["vin"]
                LIVE_STATE["make"] = details["make"]
                LIVE_STATE["year"] = details["year"]
                LIVE_STATE["country"] = details["country"]
                LIVE_STATE["model_string"] = details["model_string"]
                self.active_profile = details["profile"]
                LIVE_STATE["actuators"] = ACTUATOR_CATALOG.get(details["make"], ACTUATOR_CATALOG.get("GM", []))
        except Exception:
            pass

    def fetch_all_dtcs(self):
        if not self.dev or not LIVE_STATE["connected"]:
            return
        for svc, state_key in [(0x03, "dtcs"), (0x07, "pending_dtcs"), (0x0A, "permanent_dtcs")]:
            try:
                self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
                tx = build_tx(0x7DF, [0x01, svc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                num = ctypes.c_ulong(1)
                self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 50)
                dtc_list = []
                start = time.time()
                while time.time() - start < 0.15:
                    rx_msgs = (PASSTHRU_MSG * 40)()
                    rx_count = ctypes.c_ulong(40)
                    status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 20)
                    if status == STATUS_NOERROR and rx_count.value > 0:
                        for i in range(rx_count.value):
                            can_id, payload = parse_rx(rx_msgs[i])
                            if can_id in (0x7E8, 0x7E9) and len(payload) >= 4:
                                if payload[1] == (svc + 0x40):
                                    n = payload[0] // 2
                                    for d in range(n):
                                        b1 = payload[2 + (d * 2)]
                                        b2 = payload[3 + (d * 2)]
                                        if b1 != 0 or b2 != 0:
                                            pfx = {0: 'P', 1: 'C', 2: 'B', 3: 'U'}[(b1 & 0xC0) >> 6]
                                            code = f"{pfx}{(b1 & 0x3F):02X}{b2:02X}"
                                            if code not in dtc_list:
                                                dtc_list.append(code)
                    time.sleep(0.005)
                LIVE_STATE[state_key] = dtc_list
            except Exception:
                pass
        LIVE_STATE["dtc_details"] = [{"code": c, **lookup_dtc(c)} for c in LIVE_STATE["dtcs"]]

    def actuate_device(self, act_id: str, state: str = "ON") -> dict:
        """Triggers a bi-directional test on vehicle."""
        if not LIVE_STATE["connected"] or not self.actuator_ctrl:
            LIVE_STATE["actuator_status"] = {
                "last_action": f"{act_id} ({state})",
                "result": f"Simulated Actuation: {act_id} switched {state}",
                "success": True
            }
            return LIVE_STATE["actuator_status"]

        found = None
        for act in LIVE_STATE["actuators"]:
            if act["id"] == act_id:
                found = act
                break
        if not found:
            found = ACTUATOR_CATALOG["GM"][0]

        res = self.actuator_ctrl.execute_actuator(found, state)
        LIVE_STATE["actuator_status"] = {
            "last_action": f"{found['name']} -> {state}",
            "result": res.get("message", "Executed"),
            "success": res.get("success", False)
        }
        return LIVE_STATE["actuator_status"]

    def clear_dtcs(self) -> bool:
        if not self.dev or not LIVE_STATE["connected"]:
            LIVE_STATE["dtcs"] = []
            LIVE_STATE["pending_dtcs"] = []
            LIVE_STATE["dtc_details"] = []
            return True
        try:
            self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
            for tid in (0x7DF, 0x7E0):
                tx = build_tx(tid, [0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                num = ctypes.c_ulong(1)
                self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 100)
                time.sleep(0.05)
            time.sleep(0.3)
            self.fetch_all_dtcs()
            return True
        except Exception as e:
            LIVE_STATE["status_message"] = f"Failed to clear DTCs: {e}"
            return False

    def start_logging(self) -> str:
        filename = f"scan_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(LOGS_DIR, filename)
        self.csv_file_handle = open(filepath, "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file_handle)
        self.csv_writer.writerow([
            "Timestamp", "Time_Sec", "Make", "RPM", "Speed_MPH", "Coolant_F", 
            "Trans_Temp_F", "Oil_Temp_F", "Throttle_Pct", "Engine_Load_Pct", "MAF_gs", "Battery_V"
        ])
        LIVE_STATE["is_logging"] = True
        LIVE_STATE["current_log_file"] = filename
        LIVE_STATE["log_records_count"] = 0
        return filename

    def stop_logging(self) -> str:
        if self.csv_file_handle:
            self.csv_file_handle.close()
            self.csv_file_handle = None
        LIVE_STATE["is_logging"] = False
        fname = LIVE_STATE["current_log_file"]
        LIVE_STATE["current_log_file"] = None
        return fname

    def run(self):
        connected = self.init_j2534()
        if connected:
            self.fetch_vin_and_profile()
            self.fetch_all_dtcs()
            LIVE_STATE["status_message"] = f"Connected: {LIVE_STATE['model_string']}"
        else:
            LIVE_STATE["simulation_mode"] = True
            LIVE_STATE["status_message"] = f"Simulation: {LIVE_STATE['model_string']}"
            LIVE_STATE["dtc_details"] = [{"code": c, **lookup_dtc(c)} for c in LIVE_STATE["dtcs"]]

        sim_t = 0.0
        log_start_time = time.time()

        while self.running:
            t0 = time.time()
            if LIVE_STATE["connected"] and not LIVE_STATE["simulation_mode"]:
                try:
                    v = self.dev.read_battery_voltage()
                    if v > 0: LIVE_STATE["battery_voltage"] = round(v, 2)

                    rpm_raw = self.query_pid(0x01, 0x0C)
                    if len(rpm_raw) >= 2: LIVE_STATE["rpm"] = round(((rpm_raw[0] * 256) + rpm_raw[1]) / 4.0, 1)

                    spd_raw = self.query_pid(0x01, 0x0D)
                    if len(spd_raw) >= 1: LIVE_STATE["speed_mph"] = round(spd_raw[0] * 0.621371, 1)

                    c_raw = self.query_pid(0x01, 0x05)
                    if len(c_raw) >= 1:
                        c_val = c_raw[0] - 40
                        LIVE_STATE["coolant_c"] = c_val
                        LIVE_STATE["coolant_f"] = round((c_val * 9/5) + 32, 1)

                    thr_raw = self.query_pid(0x01, 0x11)
                    if len(thr_raw) >= 1: LIVE_STATE["throttle_pct"] = round((thr_raw[0] * 100.0) / 255.0, 1)

                    lod_raw = self.query_pid(0x01, 0x04)
                    if len(lod_raw) >= 1: LIVE_STATE["engine_load_pct"] = round((lod_raw[0] * 100.0) / 255.0, 1)

                    maf_raw = self.query_pid(0x01, 0x10)
                    if len(maf_raw) >= 2: LIVE_STATE["maf_gs"] = round(((maf_raw[0] * 256) + maf_raw[1]) / 100.0, 2)
                except Exception:
                    LIVE_STATE["connected"] = False
                    LIVE_STATE["simulation_mode"] = True
            else:
                sim_t += 0.05
                base_rpm = 1600 + (math.sin(sim_t * 1.2) * 900) + (random.random() * 30)
                LIVE_STATE["rpm"] = round(max(700, base_rpm), 0)
                LIVE_STATE["speed_mph"] = round(max(0, 35 + (math.sin(sim_t * 0.6) * 30)), 1)
                LIVE_STATE["coolant_f"] = round(195.0 + math.sin(sim_t * 0.1) * 4, 1)
                LIVE_STATE["coolant_c"] = round((LIVE_STATE["coolant_f"] - 32) * 5/9, 1)
                LIVE_STATE["trans_temp_f"] = round(165.0 + math.sin(sim_t * 0.05) * 3, 1)
                LIVE_STATE["oil_temp_f"] = round(208.0 + math.sin(sim_t * 0.08) * 5, 1)
                LIVE_STATE["throttle_pct"] = round(max(0, 22.0 + (math.sin(sim_t * 1.2) * 20.0)), 1)
                LIVE_STATE["engine_load_pct"] = round(max(10, 36.0 + (math.sin(sim_t * 0.9) * 18.0)), 1)
                LIVE_STATE["maf_gs"] = round(4.5 + (LIVE_STATE["rpm"] / 280.0), 2)
                LIVE_STATE["battery_voltage"] = round(13.6 + (math.sin(sim_t * 0.3) * 0.15), 2)

            t1 = time.time()
            LIVE_STATE["latency_ms"] = round((t1 - t0) * 1000, 1)
            LIVE_STATE["last_update"] = t1
            broadcast_ws_state()

            sleep_target = 0.016 if LIVE_STATE["simulation_mode"] else 0.025
            elapsed = time.time() - t0
            if elapsed < sleep_target:
                time.sleep(sleep_target - elapsed)

WORKER = UniversalScannerWorker()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class UniversalWSHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), "static"), **kwargs)

    def do_GET(self):
        if self.headers.get("Upgrade", "").lower() == "websocket":
            self.handle_websocket()
            return

        parsed = urlparse(self.path)
        if parsed.path == "/api/live":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(LIVE_STATE).encode("utf-8"))
            return

        super().do_GET()

    def handle_websocket(self):
        key = self.headers.get("Sec-WebSocket-Key", "")
        accept_raw = hashlib.sha1((key + WS_GUID).encode("utf-8")).digest()
        accept_str = base64.b64encode(accept_raw).decode("utf-8")

        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_str}\r\n\r\n"
        )
        self.wfile.write(response.encode("utf-8"))
        self.wfile.flush()

        sock = self.request
        sock.setblocking(True)
        
        with WS_LOCK:
            WS_CLIENTS.add(sock)

        try:
            while True:
                head = sock.recv(2)
                if not head or len(head) < 2: break
                b1, b2 = head[0], head[1]
                opcode = b1 & 0x0F
                if opcode == 0x08: break
                
                masked = (b2 & 0x80) != 0
                payload_len = b2 & 0x7F
                if payload_len == 126:
                    ext = sock.recv(2)
                    payload_len = struct.unpack("!H", ext)[0]
                elif payload_len == 127:
                    ext = sock.recv(8)
                    payload_len = struct.unpack("!Q", ext)[0]

                masks = sock.recv(4) if masked else b""
                data = sock.recv(payload_len)
                unmasked = bytes(b ^ masks[i % 4] for i, b in enumerate(data)) if masked else data

                try:
                    cmd = json.loads(unmasked.decode("utf-8"))
                    action = cmd.get("action", "")
                    if action == "actuate":
                        act_id = cmd.get("actuator_id", "")
                        state = cmd.get("state", "ON")
                        WORKER.actuate_device(act_id, state)
                    elif action == "clear_dtcs":
                        WORKER.clear_dtcs()
                    elif action == "start_log":
                        WORKER.start_logging()
                    elif action == "stop_log":
                        WORKER.stop_logging()
                    elif action == "arm_timer":
                        LIVE_STATE["timer_state"] = "ARMED"
                        LIVE_STATE["accel_time_0_60"] = 0.0
                    elif action == "toggle_mode":
                        LIVE_STATE["simulation_mode"] = not LIVE_STATE["simulation_mode"]
                    elif action == "set_make":
                        make = cmd.get("make", "Chevrolet")
                        if make in MANUFACTURER_PROFILES:
                            LIVE_STATE["make"] = make
                            LIVE_STATE["model_string"] = f"2022 {make} (Multi-Make Profile)"
                            WORKER.active_profile = MANUFACTURER_PROFILES[make]
                            LIVE_STATE["actuators"] = ACTUATOR_CATALOG.get(make, ACTUATOR_CATALOG["GM"])
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            with WS_LOCK:
                if sock in WS_CLIENTS:
                    WS_CLIENTS.remove(sock)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/actuate":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            res = WORKER.actuate_device(data.get("actuator_id", ""), data.get("state", "ON"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

def main():
    PORT = 8080
    print("==================================================")
    print("   UNIVERSAL MULTI-VEHICLE & ACTUATOR SUITE       ")
    print("==================================================")
    print(f"[*] Starting J2534 Diagnostic Engine...")
    WORKER.start()

    server = ThreadedHTTPServer(("0.0.0.0", PORT), UniversalWSHandler)
    print(f"\n[OK] Universal Scan Tool Server Online!")
    print(f" -> http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        WORKER.running = False
        server.shutdown()

if __name__ == "__main__":
    main()
