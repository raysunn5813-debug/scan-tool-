"""
======================================================================
                 SUPER SCAN TOOL - GM LIVE SCANNER
               2019 Chevrolet Traverse / GM Global-A
======================================================================
"""

import sys
import time
import os
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)

def build_tx_frame(can_id: int, payload: list) -> PASSTHRU_MSG:
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

def parse_rx_frame(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    return can_id, data[4:]

class SuperScanEngine:
    def __init__(self, dev: J2534Device, chan_id: int):
        self.dev = dev
        self.chan_id = chan_id

    def send_frame(self, can_id: int, payload: list):
        tx = build_tx_frame(can_id, payload)
        num = ctypes.c_ulong(1)
        self.dev.dll.PassThruWriteMsgs(self.chan_id, ctypes.byref(tx), ctypes.byref(num), 50)

    def query_pid(self, service: int, pid: int, target_id: int = 0x7E0, timeout_sec: float = 0.08) -> list:
        """Query standard OBD-II PID with GM 0x00 padding."""
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        
        # Send [Length=2, Service, PID, 0, 0, 0, 0, 0]
        self.send_frame(target_id, [0x02, service, pid, 0x00, 0x00, 0x00, 0x00, 0x00])

        start = time.time()
        while time.time() - start < timeout_sec:
            rx_msgs = (PASSTHRU_MSG * 50)()
            rx_count = ctypes.c_ulong(50)
            status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 15)

            if status == STATUS_NOERROR and rx_count.value > 0:
                for i in range(rx_count.value):
                    can_id, payload = parse_rx_frame(rx_msgs[i])
                    # ECM is 0x7E8, TCM is 0x7E9, ABS is 0x7EA
                    if can_id in (0x7E8, 0x7E9, 0x7EA) and len(payload) >= 3:
                        if payload[1] == (service + 0x40) and payload[2] == pid:
                            return list(payload[3:])
            time.sleep(0.002)
        return []

    def get_vin(self) -> str:
        """Fetch 17-character VIN with ISO-TP flow control."""
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        self.send_frame(0x7E0, [0x02, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        vin_bytes = bytearray()
        start = time.time()

        while time.time() - start < 0.6:
            rx_msgs = (PASSTHRU_MSG * 50)()
            rx_count = ctypes.c_ulong(50)
            status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 20)

            if status == STATUS_NOERROR and rx_count.value > 0:
                for i in range(rx_count.value):
                    can_id, payload = parse_rx_frame(rx_msgs[i])
                    if can_id == 0x7E8 and len(payload) >= 5:
                        pci_type = (payload[0] & 0xF0) >> 4

                        # Single Frame
                        if pci_type == 0x00 and payload[1] == 0x49 and payload[2] == 0x02:
                            vin_bytes.extend(payload[4:])
                            break

                        # First Frame (ISO-TP)
                        elif pci_type == 0x01 and payload[2] == 0x49 and payload[3] == 0x02:
                            vin_bytes.extend(payload[5:])
                            # Send Flow Control (CTS) back to ECM
                            self.send_frame(0x7E0, [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

                        # Consecutive Frame
                        elif pci_type == 0x02:
                            vin_bytes.extend(payload[1:])
                            if len(vin_bytes) >= 17:
                                break
            if len(vin_bytes) >= 17:
                break
            time.sleep(0.005)

        vin = "".join([chr(b) for b in vin_bytes if 32 <= b <= 126]).strip()
        return vin if len(vin) >= 11 else "Unknown"

    def read_dtcs(self) -> list:
        """Read confirmed Diagnostic Trouble Codes (Mode 03)."""
        self.dev.dll.PassThruIoctl(self.chan_id, CLEAR_RX_BUFFER, None, None)
        self.send_frame(0x7DF, [0x01, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        dtcs = []
        start = time.time()
        while time.time() - start < 0.2:
            rx_msgs = (PASSTHRU_MSG * 50)()
            rx_count = ctypes.c_ulong(50)
            status = self.dev.dll.PassThruReadMsgs(self.chan_id, rx_msgs, ctypes.byref(rx_count), 20)
            if status == STATUS_NOERROR and rx_count.value > 0:
                for i in range(rx_count.value):
                    can_id, payload = parse_rx_frame(rx_msgs[i])
                    if can_id in (0x7E8, 0x7E9) and len(payload) >= 4:
                        if payload[1] == 0x43: # Mode 03 response
                            num_dtcs = payload[0] // 2
                            for d_idx in range(num_dtcs):
                                b1 = payload[2 + (d_idx * 2)]
                                b2 = payload[3 + (d_idx * 2)]
                                if b1 != 0 or b2 != 0:
                                    prefix = {0: 'P', 1: 'C', 2: 'B', 3: 'U'}[(b1 & 0xC0) >> 6]
                                    code = f"{prefix}{(b1 & 0x3F):02X}{b2:02X}"
                                    dtcs.append((can_id, code))
            time.sleep(0.005)
        return dtcs

def main():
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
        chan_id = dev.connect(protocol_id=CAN, baudrate=500000)

        # Open wide pass filter
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        mask = PASSTHRU_MSG()
        mask.ProtocolID = CAN
        mask.DataSize = 4
        pattern = PASSTHRU_MSG()
        pattern.ProtocolID = CAN
        pattern.DataSize = 4
        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))

        engine = SuperScanEngine(dev, chan_id)

        print("\n" + "="*65)
        print("          SUPER SCAN TOOL - 2019 CHEVROLET TRAVERSE       ")
        print("="*65)
        print(f"[*] Battery Voltage:   {vbatt:.2f} V")
        
        vin = engine.get_vin()
        print(f"[*] Vehicle VIN:       {vin}")

        dtcs = engine.read_dtcs()
        if dtcs:
            print(f"[!] Fault Codes:       {', '.join([c for _, c in dtcs])}")
        else:
            print("[*] Fault Codes (DTC): No Active DTCs (System Clean)")

        print("="*65)
        print("       LIVE DATA DASHBOARD STREAM (Press Ctrl+C to Stop)  ")
        print("="*65)

        sample_count = 0
        while sample_count < 30:
            sample_count += 1
            # 1. RPM (0x0C)
            rpm_raw = engine.query_pid(service=0x01, pid=0x0C)
            rpm = ((rpm_raw[0] * 256) + rpm_raw[1]) / 4.0 if len(rpm_raw) >= 2 else 0

            # 2. Coolant (0x05)
            cool_raw = engine.query_pid(service=0x01, pid=0x05)
            cool_c = (cool_raw[0] - 40) if len(cool_raw) >= 1 else 0
            cool_f = (cool_c * 9/5) + 32

            # 3. Vehicle Speed (0x0D)
            spd_raw = engine.query_pid(service=0x01, pid=0x0D)
            spd_mph = (spd_raw[0] * 0.621371) if len(spd_raw) >= 1 else 0

            # 4. Throttle (0x11)
            thr_raw = engine.query_pid(service=0x01, pid=0x11)
            thr_pct = ((thr_raw[0] * 100.0) / 255.0) if len(thr_raw) >= 1 else 0

            # 5. Engine Load (0x04)
            load_raw = engine.query_pid(service=0x01, pid=0x04)
            load_pct = ((load_raw[0] * 100.0) / 255.0) if len(load_raw) >= 1 else 0

            # Visual bar for RPM
            rpm_bar_len = int(rpm / 150)
            rpm_bar = "█" * min(rpm_bar_len, 25)

            sys.stdout.write(
                f"\r[#{sample_count:02d}] RPM: {rpm:4.0f} |{rpm_bar:<25}|  Coolant: {cool_f:5.1f}°F  Speed: {spd_mph:3.0f} MPH  Throttle: {thr_pct:4.1f}%  Load: {load_pct:4.1f}%"
            )
            sys.stdout.flush()
            time.sleep(0.12)

        print("\n\n[OK] Stream session finished successfully.")

    except KeyboardInterrupt:
        print("\n\n[*] Stream stopped by user.")
    finally:
        dev.disconnect()
        dev.close()
        print("[OK] J2534 Hardware disconnected.")

if __name__ == "__main__":
    main()
