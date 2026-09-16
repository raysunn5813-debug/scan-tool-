"""
Comprehensive ECU Diagnostic Prober
Tests various padding schemes (0x00, 0x55, None), DLCs, and diagnostic addresses.
Displays all response frames in real-time.
"""

import sys
import time
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)

def build_msg(can_id: int, payload: bytes) -> PASSTHRU_MSG:
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

def parse_msg(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    return can_id, data[4:]

def main():
    print("==================================================")
    print("      COMPREHENSIVE ECU DIAGNOSTIC PROBER         ")
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

        # Pass-ALL Filter (so we don't accidentally filter out ECU replies)
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        mask = PASSTHRU_MSG()
        mask.ProtocolID = CAN
        mask.DataSize = 4
        pattern = PASSTHRU_MSG()
        pattern.ProtocolID = CAN
        pattern.DataSize = 4
        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))

        # Diagnostic IDs to test
        target_ids = [
            (0x7DF, "OBD2 11-bit Broadcast"),
            (0x7E0, "PCM / Engine Physical"),
            (0x7E1, "TCM / Transmission Physical"),
            (0x7E2, "Chassis / ABS Physical"),
            (0x720, "Ford Cluster / Gateway Physical"),
            (0x7E4, "Body Control Module Physical")
        ]

        # Padding formats:
        paddings = [
            ("Padded with 0x00 (8-byte)", bytes([0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])),
            ("Padded with 0x55 (8-byte)", bytes([0x02, 0x01, 0x00, 0x55, 0x55, 0x55, 0x55, 0x55])),
            ("Padded with 0xAA (8-byte)", bytes([0x02, 0x01, 0x00, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA])),
            ("Unpadded (3-byte DLC)",     bytes([0x02, 0x01, 0x00]))
        ]

        print("\n[*] Probing ECUs with Mode 01 PID 00 (Supported PIDs)...")
        found_any = False

        for target_id, target_desc in target_ids:
            for pad_name, payload in paddings:
                # Flush RX buffer
                dev.dll.PassThruIoctl(chan_id, CLEAR_RX_BUFFER, None, None)
                
                # Send frame
                tx_msg = build_msg(target_id, payload)
                num = ctypes.c_ulong(1)
                dev.dll.PassThruWriteMsgs(chan_id, ctypes.byref(tx_msg), ctypes.byref(num), 100)

                # Read all frames for next 80ms
                start = time.time()
                while time.time() - start < 0.08:
                    rx_msgs = (PASSTHRU_MSG * 50)()
                    rx_count = ctypes.c_ulong(50)
                    status = dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 20)
                    
                    if status == STATUS_NOERROR and rx_count.value > 0:
                        for i in range(rx_count.value):
                            can_id, rx_data = parse_msg(rx_msgs[i])
                            # Diagnostic responses are typically in 0x7E8-0x7EF or 0x500-0x7FF with 0x41 response
                            if 0x7E8 <= can_id <= 0x7EF or (len(rx_data) > 1 and 0x41 in rx_data):
                                print(f"\n[!!! ECU FOUND !!!]")
                                print(f"    Target:  0x{target_id:03X} ({target_desc})")
                                print(f"    Format:  {pad_name}")
                                print(f"    ECU ID:  0x{can_id:03X}")
                                print(f"    Payload: {rx_data.hex(' ')}")
                                found_any = True
                                break
                    if found_any:
                        break
                if found_any:
                    break
            if found_any:
                break

        if not found_any:
            print("\n[-] Standard 11-bit queries did not trigger 0x7E8. Let's check for UDS TesterPresent (0x3E 0x00)...")
            # Try UDS TesterPresent
            uds_msg = build_msg(0x7E0, bytes([0x02, 0x3E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
            num = ctypes.c_ulong(1)
            dev.dll.PassThruWriteMsgs(chan_id, ctypes.byref(uds_msg), ctypes.byref(num), 100)
            time.sleep(0.05)
            rx_msgs = (PASSTHRU_MSG * 50)()
            rx_count = ctypes.c_ulong(50)
            dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 50)
            for i in range(rx_count.value):
                can_id, rx_data = parse_msg(rx_msgs[i])
                if 0x700 <= can_id <= 0x7FF:
                    print(f"    UDS Frame from 0x{can_id:03X}: {rx_data.hex(' ')}")

    finally:
        dev.disconnect()
        dev.close()
        print("\n[OK] Probe finished.")

if __name__ == "__main__":
    main()
