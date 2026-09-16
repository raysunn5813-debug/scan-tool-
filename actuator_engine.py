"""
Universal Bi-Directional Actuator & Module Control Engine
Supports UDS Service 0x2F (InputOutputControlByIdentifier), 0x10 Diagnostic Session Control, 
0x3E TesterPresent keep-alive, and GM/Ford/Toyota/Honda/VW/Nissan actuator commands.
"""

import time
import ctypes
import threading
from j2534_client import (
    J2534Device, PASSTHRU_MSG, CAN, STATUS_NOERROR, CLEAR_RX_BUFFER
)

UDS_NRC_DESCRIPTIONS = {
    0x11: "Service Not Supported in current diagnostic session (Must enter Extended Session 0x10 0x03)",
    0x12: "Sub-function Not Supported / Invalid Control Parameter",
    0x13: "Incorrect Message Length or Invalid Format",
    0x22: "Conditions Not Correct (Vehicle Engine must be OFF with Ignition ON - KOEO)",
    0x31: "Request Out of Range (Parameter / DID not recognized by this ECU)",
    0x33: "Security Access Denied (ECU Seed/Key unlock required)",
    0x35: "Invalid Key Supplied",
    0x36: "Exceeded Number of Attempts (Security Lockout)",
    0x78: "Response Pending (ECU is processing command)",
    0x7E: "Sub-function Not Supported in Active Session",
    0x7F: "General Service Not Supported"
}

ACTUATOR_CATALOG = {
    # General Motors / Chevy / GMC
    "GM": [
        {
            "id": "gm_fan_relay",
            "name": "Radiator Cooling Fan Relay",
            "module": "Engine Control Module (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x20, 0x03, 0x64],      # 0x2F DID 0x0120 100% On
            "cmd_off": [0x2F, 0x01, 0x20, 0x00],            # 0x2F ReturnControlToECU
            "alt_on": [0xAE, 0x01, 0x01, 0x01],             # GM Mode 0xAE Fan Relay
            "alt_off": [0xAE, 0x01, 0x00, 0x00],
            "description": "Engages High/Low speed cooling fan relays to test fan motors & wiring."
        },
        {
            "id": "gm_fuel_pump",
            "name": "Fuel Pump Relay Test",
            "module": "Engine Control Module (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x1A, 0x03, 0x01],
            "cmd_off": [0x2F, 0x01, 0x1A, 0x00],
            "alt_on": [0xAE, 0x02, 0x01, 0x01],
            "alt_off": [0xAE, 0x02, 0x00, 0x00],
            "description": "Primes and runs fuel pump relay to verify pressure & pump prime sound."
        },
        {
            "id": "gm_ac_clutch",
            "name": "A/C Compressor Clutch Relay",
            "module": "Engine Control Module (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x30, 0x03, 0x01],
            "cmd_off": [0x2F, 0x01, 0x30, 0x00],
            "alt_on": [0xAE, 0x03, 0x01, 0x01],
            "alt_off": [0xAE, 0x03, 0x00, 0x00],
            "description": "Clicks the A/C clutch magnetic coil to test compressor engagement."
        },
        {
            "id": "gm_evap_purge",
            "name": "EVAP Purge Solenoid Valve",
            "module": "Engine Control Module (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x14, 0x03, 0x32],      # 50% Duty cycle
            "cmd_off": [0x2F, 0x01, 0x14, 0x00],
            "alt_on": [0x08, 0x01, 0x00, 0x00],             # OBD Mode 08
            "alt_off": [0x08, 0x00, 0x00, 0x00],
            "description": "Pulses the evaporative purge valve to test for canister vacuum leaks."
        },
        {
            "id": "gm_evap_vent",
            "name": "EVAP Vent Solenoid Valve",
            "module": "Engine Control Module (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x15, 0x03, 0x01],
            "cmd_off": [0x2F, 0x01, 0x15, 0x00],
            "description": "Seals the gas tank vent solenoid to perform EVAP leak checks."
        },
        {
            "id": "gm_cluster_sweep",
            "name": "Instrument Cluster Needle Sweep",
            "module": "Instrument Panel (0x720 / CGM 0x241)",
            "can_id": 0x720,
            "resp_id": 0x728,
            "session": 0x03,
            "cmd_on": [0x2F, 0x02, 0x01, 0x03, 0xFF],
            "cmd_off": [0x2F, 0x02, 0x01, 0x00],
            "description": "Sweeps speedometer and tachometer needles from 0 to maximum."
        }
    ],

    # Ford / Lincoln
    "Ford": [
        {
            "id": "ford_high_fan",
            "name": "High Speed Cooling Fan",
            "module": "PCM (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x40, 0x03, 0x01],
            "cmd_off": [0x2F, 0x01, 0x40, 0x00],
            "description": "Engages Ford PCM High Speed Fan Output."
        },
        {
            "id": "ford_fuel_pump",
            "name": "Fuel Pump Driver Module (FPDM)",
            "module": "PCM (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x2F, 0x01, 0x1B, 0x03, 0x01],
            "cmd_off": [0x2F, 0x01, 0x1B, 0x00],
            "description": "Activates Ford electronic fuel pump driver."
        }
    ],

    # Toyota / Lexus
    "Toyota": [
        {
            "id": "toyota_fan_relay",
            "name": "Electric Radiator Fan",
            "module": "ECM (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x30, 0x01, 0x00, 0x01],
            "cmd_off": [0x30, 0x01, 0x00, 0x00],
            "description": "Toyota Active Test Service 0x30: Cooling Fan Relay."
        },
        {
            "id": "toyota_fuel_pump",
            "name": "Fuel Pump Circuit Opening Relay",
            "module": "ECM (0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x30, 0x02, 0x00, 0x01],
            "cmd_off": [0x30, 0x02, 0x00, 0x00],
            "description": "Toyota Active Test Service 0x30: Fuel Pump Activation."
        }
    ],

    # Universal OBD-II Actuators
    "Universal": [
        {
            "id": "univ_evap_leak",
            "name": "OBD-II Mode 08 EVAP Leak Test",
            "module": "Universal ECM (0x7DF / 0x7E0)",
            "can_id": 0x7E0,
            "resp_id": 0x7E8,
            "session": 0x03,
            "cmd_on": [0x08, 0x01, 0x00, 0x00],
            "cmd_off": [0x08, 0x00, 0x00, 0x00],
            "description": "Triggers onboard standard SAE J1979 Mode 08 component test."
        }
    ]
}

def build_tx_msg(can_id: int, payload: list) -> PASSTHRU_MSG:
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

def parse_rx_msg(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    return can_id, data[4:]

class ActuatorController:
    def __init__(self, dev: J2534Device, chan_id: int):
        self.dev = dev
        self.chan_id = chan_id
        self.keep_alive_running = False
        self.keep_alive_thread = None
        self.target_can_id = 0x7E0

    def _send_can(self, can_id: int, payload: list):
        tx = build_tx_msg(can_id, payload)
        num = ctypes.c_ulong(1)
        self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 50)

    def _recv_can(self, timeout_ms: int = 100):
        start = time.time()
        while (time.time() - start) * 1000 < timeout_ms:
            rx_msgs = (PASSTHRU_MSG * 40)()
            rx_count = ctypes.c_ulong(40)
            status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 20)
            if status == STATUS_NOERROR and rx_count.value > 0:
                for i in range(rx_count.value):
                    can_id, payload = parse_rx_msg(rx_msgs[i])
                    if can_id in (0x7E8, 0x7E9, 0x7EA, 0x7EB, 0x728, 0x641) and len(payload) >= 2:
                        return can_id, list(payload)
            time.sleep(0.003)
        return None, []

    def start_keep_alive(self, target_can_id: int = 0x7E0):
        """Sends UDS TesterPresent (0x3E 0x80) periodically to hold diagnostic session."""
        self.target_can_id = target_can_id
        if self.keep_alive_running:
            return
        self.keep_alive_running = True
        
        def loop():
            while self.keep_alive_running:
                try:
                    self._send_can(self.target_can_id, [0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00])
                except Exception:
                    pass
                time.sleep(1.5)

        self.keep_alive_thread = threading.Thread(target=loop, daemon=True)
        self.keep_alive_thread.start()

    def stop_keep_alive(self):
        self.keep_alive_running = False

    def enter_extended_session(self, target_id: int = 0x7E0) -> dict:
        """Transmits UDS Service 0x10 (DiagnosticSessionControl 0x03 Extended)."""
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        self._send_can(target_id, [0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        can_id, rx = self._recv_can(timeout_ms=150)
        
        if not rx:
            return {"success": False, "message": "No response from ECU (Check ignition ON)"}
        
        # Check positive ack (0x50 0x03)
        if len(rx) >= 2 and (rx[1] == 0x50 or rx[0] == 0x50):
            self.start_keep_alive(target_id)
            return {"success": True, "message": "UDS Extended Diagnostic Session 0x03 Established!"}
        
        # Check Negative Response (0x7F 0x10 NRC)
        if len(rx) >= 3 and rx[1] == 0x7F:
            nrc = rx[3] if len(rx) >= 4 else rx[2]
            reason = UDS_NRC_DESCRIPTIONS.get(nrc, f"ECU Rejected (NRC 0x{nrc:02X})")
            return {"success": False, "message": reason}

        return {"success": True, "message": f"Session response received: {' '.join(f'{b:02X}' for b in rx)}"}

    def execute_actuator(self, act_config: dict, state: str = "ON") -> dict:
        """Executes a bi-directional actuator test command."""
        target_id = act_config["can_id"]
        
        # Step 1: Guarantee Extended Diagnostic Session
        sess_res = self.enter_extended_session(target_id)
        
        # Step 2: Choose command payload
        raw_cmd = act_config["cmd_on"] if state == "ON" else act_config["cmd_off"]
        pci_len = len(raw_cmd)
        padded = [pci_len] + raw_cmd + [0x00] * (7 - pci_len)
        
        # Step 3: Transmit actuation frame
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        self._send_can(target_id, padded[:8])
        can_id, rx = self._recv_can(timeout_ms=250)

        # Fallback to alternate command if rejected
        if (not rx or (len(rx) >= 2 and rx[1] == 0x7F)) and "alt_on" in act_config:
            alt_cmd = act_config["alt_on"] if state == "ON" else act_config["alt_off"]
            pci_alt = len(alt_cmd)
            padded_alt = [pci_alt] + alt_cmd + [0x00] * (7 - pci_alt)
            self._send_can(target_id, padded_alt[:8])
            can_id, rx = self._recv_can(timeout_ms=250)

        if not rx:
            return {
                "success": False,
                "state": state,
                "message": "⚠️ No response from ECU. Make sure Ignition is in KOEO (Key On, Engine Off) position."
            }

        # Check positive ack (Service + 0x40)
        svc = raw_cmd[0]
        if len(rx) >= 2 and rx[1] == (svc + 0x40):
            return {
                "success": True,
                "state": state,
                "message": f"✅ SUCCESS: {act_config['name']} commanded {state}! (ECU ACK 0x{rx[1]:02X})",
                "rx_hex": " ".join(f"{b:02X}" for b in rx)
            }

        # Check NRC
        if len(rx) >= 3 and rx[1] == 0x7F:
            nrc = rx[3] if len(rx) >= 4 else rx[2]
            reason = UDS_NRC_DESCRIPTIONS.get(nrc, f"ECU Rejected command (NRC 0x{nrc:02X})")
            return {
                "success": False,
                "state": state,
                "message": f"⚠️ ECU Rejected Actuation: {reason}",
                "rx_hex": " ".join(f"{b:02X}" for b in rx)
            }

        return {
            "success": True,
            "state": state,
            "message": f"ECU Responded: {' '.join(f'{b:02X}' for b in rx)}",
            "rx_hex": " ".join(f"{b:02X}" for b in rx)
        }
