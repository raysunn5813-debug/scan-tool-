"""
2019 Chevrolet Traverse Live Diagnostic Scanner (Fixed J2534 Filter Mask)
Handles GM 500k HS-CAN, ISO-TP Multi-Frame VIN decoding, and Real-Time Live Sensor Streaming.
"""

import sys
import time
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)

def build_tx_msg(can_id: int, payload: list) -> PASSTHRU_MSG:
    """Build standard 8-byte CAN frame for transmission."""
    msg = PASSTHRU_MSG()
    msg.ProtocolID = CAN
    msg.TxFlags = 0
    msg.DataSize = 4 + 8  # 4 bytes CAN ID + 8 bytes payload
    msg.Data[0] = (can_id >> 24) & 0xFF
    msg.Data[1] = (can_id >> 16) & 0xFF
    msg.Data[2] = (can_id >> 8) & 0xFF
    msg.Data[3] = can_id & 0xFF
    
    # Pad payload to 8 bytes with 0x00
    while len(payload) < 8:
        payload.append(0x00)
    for i in range(8):
        msg.Data[4 + i] = payload[i]
    return msg

def build_filter_msg(can_id: int) -> PASSTHRU_MSG:
    """Build 4-byte CAN ID header for filter mask/pattern."""
    msg = PASSTHRU_MSG()
    msg.ProtocolID = CAN
    msg.TxFlags = 0
    msg.DataSize = 4  # ONLY 4 bytes for CAN ID match
    msg.Data[0] = (can_id >> 24) & 0xFF
    msg.Data[1] = (can_id >> 16) & 0xFF
    msg.Data[2] = (can_id >> 8) & 0xFF
    msg.Data[3] = can_id & 0xFF
    return msg

def parse_can_frame(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    return can_id, data[4:]

class GMScanner:
    def __init__(self, dev: J2534Device, chan_id: int):
        self.dev = dev
        self.chan_id = chan_id

    def send_raw(self, can_id: int, payload: list):
        tx = build_tx_msg(can_id, payload)
        num = ctypes.c_ulong(1)
        self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 100)

    def query_pid(self, service: int, pid: int, target_id: int = 0x7DF, timeout_ms: int = 200) -> dict:
        """Send Mode 01 request and wait for 0x7E8/0x7E9 response."""
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_TX_BUFFER, None, None)
        
        # Standard GM OBD request: [Length=2, Service, PID, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.send_raw(target_id, [0x02, service, pid, 0x00, 0x00, 0x00, 0x00, 0x00])

        start = time.time()
        while (time.time() - start) * 1000 < timeout_ms:
            rx_msgs = (PASSTHRU_MSG * 40)()
            rx_count = ctypes.c_ulong(40)
            status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 30)
            
            if status == STATUS_NOERROR and rx_count.value > 0:
                for i in range(rx_count.value):
                    can_id, payload = parse_can_frame(rx_msgs[i])
                    if can_id in (0x7E8, 0x7E9, 0x7EA, 0x7EB) and len(payload) >= 3:
                        # Positive response: 0x40 + service
                        if (payload[1] == (service + 0x40) and payload[2] == pid) or (payload[0] == (service + 0x40) and payload[1] == pid):
                            data_idx = 3 if payload[1] == (service + 0x40) else 2
                            return {"ecu_id": can_id, "data": payload[data_idx:]}
            time.sleep(0.005)
        return {}

    def get_vin(self, target_id: int = 0x7DF) -> str:
        """Read 17-character VIN using ISO-TP multi-frame flow control."""
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        self.send_raw(target_id, [0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        vin_bytes = bytearray()
        start = time.time()

        while time.time() - start < 1.0:
            rx_msgs = (PASSTHRU_MSG * 40)()
            rx_count = ctypes.c_ulong(40)
            status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 40)

            if status == STATUS_NOERROR and rx_count.value > 0:
                for i in range(rx_count.value):
                    can_id, payload = parse_can_frame(rx_msgs[i])
                    if can_id in (0x7E8, 0x7E9) and len(payload) >= 6:
                        pci_type = (payload[0] & 0xF0) >> 4
                        
                        # Single Frame VIN
                        if pci_type == 0x00 and payload[1] == 0x49 and payload[2] == 0x02:
                            vin_bytes.extend(payload[4:])
                            break

                        # First Frame (ISO-TP)
                        elif pci_type == 0x01 and payload[2] == 0x49 and payload[3] == 0x02:
                            vin_bytes.extend(payload[5:])
                            # Send Flow Control (CTS) back to ECM
                            resp_id = 0x7E0 if can_id == 0x7E8 else 0x7E1
                            self.send_raw(resp_id, [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

                        # Consecutive Frames
                        elif pci_type == 0x02:
                            vin_bytes.extend(payload[1:])
                            if len(vin_bytes) >= 17:
                                break
            if len(vin_bytes) >= 17:
                break
            time.sleep(0.005)

        vin = "".join([chr(b) for b in vin_bytes if 32 <= b <= 126]).strip()
        return vin if len(vin) >= 11 else ("No response" if not vin_bytes else f"Raw: {bytes(vin_bytes).hex(' ')}")

def main():
    print("==================================================")
    print("   2019 CHEVROLET TRAVERSE - SUPER SCAN TOOL      ")
    print("==================================================")

    devices = get_installed_j2534_devices()
    selected_device = None
    for dev in devices:
        if "PassThru464.dll" in dev["dll_path"]:
            selected_device = dev
            break
    if not selected_device:
        selected_device = devices[0]

    dev = J2534Device(selected_device["dll_path"])
    dev.open()

    try:
        vbatt = dev.read_battery_voltage()
        print(f"[OK] OBD-II Battery Voltage: {vbatt:.2f} V")

        chan_id = dev.connect(protocol_id=CAN, baudrate=500000)
        print(f"[OK] CAN 500k Channel Connected (ID: {chan_id})")

        # Configure J2534 filter for 0x7E8 - 0x7EF (4 bytes DataSize ONLY)
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        mask = build_filter_msg(0x000007F8)     # Matches 0x7E8 - 0x7EF
        pattern = build_filter_msg(0x000007E8)  # Target 0x7E8
        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))
        print("[OK] GM ECM/TCM CAN Filter (0x7E8-0x7EF) Active.\n")

        scanner = GMScanner(dev, chan_id)

        # 1. VIN
        print("[*] Reading Vehicle VIN (Mode 09)...")
        vin = scanner.get_vin()
        print(f"    -> VIN: {vin}\n")

        # 2. Live Data Loop
        print("="*60)
        print("    STARTING LIVE SENSOR STREAM (Press Ctrl+C to stop)")
        print("="*60)

        for _ in range(15):
            # RPM
            rpm_res = scanner.query_pid(service=0x01, pid=0x0C)
            rpm_val = "N/A"
            if rpm_res and len(rpm_res["data"]) >= 2:
                rpm = ((rpm_res["data"][0] * 256) + rpm_res["data"][1]) / 4.0
                rpm_val = f"{rpm:.0f} RPM"

            # Coolant
            cool_res = scanner.query_pid(service=0x01, pid=0x05)
            cool_val = "N/A"
            if cool_res and len(cool_res["data"]) >= 1:
                c = cool_res["data"][0] - 40
                f = (c * 9/5) + 32
                cool_val = f"{f:.1f} °F ({c} °C)"

            # Speed
            spd_res = scanner.query_pid(service=0x01, pid=0x0D)
            spd_val = "N/A"
            if spd_res and len(spd_res["data"]) >= 1:
                mph = spd_res["data"][0] * 0.621371
                spd_val = f"{mph:.1f} MPH"

            # Throttle
            thr_res = scanner.query_pid(service=0x01, pid=0x11)
            thr_val = "N/A"
            if thr_res and len(thr_res["data"]) >= 1:
                pct = (thr_res["data"][0] * 100.0) / 255.0
                thr_val = f"{pct:.1f}%"

            # Load
            load_res = scanner.query_pid(service=0x01, pid=0x04)
            load_val = "N/A"
            if load_res and len(load_res["data"]) >= 1:
                lpct = (load_res["data"][0] * 100.0) / 255.0
                load_val = f"{lpct:.1f}%"

            print(f"[LIVE] RPM: {rpm_val:<10} | Coolant: {cool_val:<16} | Speed: {spd_val:<9} | Throttle: {thr_val:<6} | Load: {load_val}")
            time.sleep(0.2)

        print("\n[OK] Stream test complete.")

    except KeyboardInterrupt:
        print("\n[*] Stopping stream...")
    finally:
        dev.disconnect()
        dev.close()
        print("[OK] Device closed cleanly.")

if __name__ == "__main__":
    main()
