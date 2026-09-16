"""
GM Diagnostic Address & Gateway Sweep
Sweeps functional and physical request IDs across the 2019 Traverse CAN bus with zero filtering.
"""

import sys
import time
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)

def build_raw_frame(can_id: int, payload: list) -> PASSTHRU_MSG:
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

def parse_raw_frame(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    return can_id, data[4:]

def main():
    print("==================================================")
    print("      GM TRAVERSE DIAGNOSTIC GATEWAY SWEEP        ")
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
        print(f"[OK] Pin 16 Battery Voltage: {vbatt:.2f} V")

        chan_id = dev.connect(protocol_id=CAN, baudrate=500000)
        print(f"[OK] CAN 500k Connected (Channel ID: {chan_id})")

        # Open wide pass filter (Mask=0, Pattern=0)
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        mask = PASSTHRU_MSG()
        mask.ProtocolID = CAN
        mask.DataSize = 4
        pattern = PASSTHRU_MSG()
        pattern.ProtocolID = CAN
        pattern.DataSize = 4
        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))

        # Test Addresses
        test_targets = [
            (0x7DF, "Broadcast 0x7DF", [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            (0x7E0, "Physical ECM 0x7E0", [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            (0x7E1, "Physical TCM 0x7E1", [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            (0x7E2, "Physical ABS 0x7E2", [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            (0x7DF, "Broadcast Unpadded", [0x02, 0x01, 0x00]),
            (0x7E0, "Physical ECM Unpadded", [0x02, 0x01, 0x00]),
            (0x7E0, "UDS ReadDataById (VIN 0xF190)", [0x03, 0x22, 0xF1, 0x90, 0x00, 0x00, 0x00, 0x00]),
            (0x7E0, "UDS DiagnosticSession 0x01", [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]),
            (0x241, "GM Gateway Functional 0x241", [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
        ]

        print("\n[*] Sending diagnostic queries...")
        for can_id, label, payload in test_targets:
            # Clear RX buffer
            dev.dll.PassThruIoctl(chan_id, CLEAR_RX_BUFFER, None, None)
            
            # Send
            tx = build_raw_frame(can_id, payload)
            num = ctypes.c_ulong(1)
            dev.dll.PassThruWriteMsgs(chan_id, ctypes.byref(tx), ctypes.byref(num), 100)

            # Read back
            start = time.time()
            diag_responses = []
            while time.time() - start < 0.1:
                rx_msgs = (PASSTHRU_MSG * 40)()
                rx_count = ctypes.c_ulong(40)
                status = dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 20)
                if status == STATUS_NOERROR and rx_count.value > 0:
                    for i in range(rx_count.value):
                        cid, pld = parse_raw_frame(rx_msgs[i])
                        # Detect any diagnostic response (0x7E8..0x7EF, 0x600..0x7FF, or contains 0x41/0x62/0x50/0x7F)
                        if 0x7E8 <= cid <= 0x7EF or (len(pld) >= 2 and pld[1] in (0x41, 0x62, 0x50, 0x7F)):
                            diag_responses.append((cid, pld))
                if diag_responses:
                    break

            if diag_responses:
                print(f"\n[+] SUCCESS on {label} (0x{can_id:03X})!")
                for cid, pld in diag_responses:
                    print(f"    <- Response from 0x{cid:03X}: {pld.hex(' ')}")
            else:
                print(f"    [-] No response on {label}")

    finally:
        dev.disconnect()
        dev.close()
        print("\n[OK] Sweep complete.")

if __name__ == "__main__":
    main()
