"""
Bi-Directional Actuation Diagnostic Inspector
Captures raw byte-level response from GM ECM (0x7E0) and ABS (0x7E2) for all control services.
"""

import sys
import time
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)

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

def test_command(dev, chan_id, label, target_id, payload):
    print(f"\n[*] Testing: {label} on 0x{target_id:03X}")
    print(f"    TX Frame: {bytes(payload).hex(' ')}")
    
    dev.dll.PassThruIoctl(chan_id, CLEAR_RX_BUFFER, None, None)
    tx = build_tx(target_id, payload)
    num = ctypes.c_ulong(1)
    dev.dll.PassThruWriteMsgs(chan_id, ctypes.byref(tx), ctypes.byref(num), 50)
    
    start = time.time()
    resps = []
    while time.time() - start < 0.15:
        rx_msgs = (PASSTHRU_MSG * 40)()
        rx_count = ctypes.c_ulong(40)
        status = dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 20)
        if status == STATUS_NOERROR and rx_count.value > 0:
            for i in range(rx_count.value):
                cid, pld = parse_rx(rx_msgs[i])
                if cid in (0x7E8, 0x7EA, 0x641, target_id + 8):
                    resps.append((cid, pld))
        if resps:
            break
        time.sleep(0.005)

    if resps:
        for cid, pld in resps:
            print(f"    <- RX from 0x{cid:03X}: {pld.hex(' ')}")
            # Check for NRC
            if len(pld) >= 4 and pld[1] == 0x7F:
                svc = pld[2]
                nrc = pld[3]
                print(f"       [!] Negative Response (NRC 0x{nrc:02X}) on Service 0x{svc:02X}")
                if nrc == 0x33:
                    print("           -> Reason: Security Access Required (Module is Locked)")
                elif nrc == 0x22:
                    print("           -> Reason: Conditions Not Correct (Vehicle must be in specific state)")
                elif nrc == 0x7E or nrc == 0x11:
                    print("           -> Reason: Service Not Allowed in current session")
            elif len(pld) >= 2 and pld[1] in (payload[1] + 0x40, 0x50, 0x6F, 0x71):
                print(f"       [+] POSITIVE ACK: Command Executed Successfully!")
    else:
        print("    [-] No response from module (Module not on this bus or asleep).")

def main():
    devices = get_installed_j2534_devices()
    selected = None
    for d in devices:
        if "PassThru464.dll" in d["dll_path"]:
            selected = d
            break
    if not selected:
        selected = devices[0]

    dev = J2534Device(selected["dll_path"])
    dev.open()

    try:
        chan_id = dev.connect(protocol_id=CAN, baudrate=500000)
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        mask = PASSTHRU_MSG()
        mask.ProtocolID = CAN
        mask.DataSize = 4
        pattern = PASSTHRU_MSG()
        pattern.ProtocolID = CAN
        pattern.DataSize = 4
        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))

        print("==================================================")
        print("    BI-DIRECTIONAL & UDS SECURITY PROBER          ")
        print("==================================================")

        # 1. Test Mode 08 (Standard OBD-II Actuator Control)
        test_command(dev, chan_id, "OBD Mode 08 (Evap Purge / Actuator Control)", 0x7E0, [0x02, 0x08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])

        # 2. Test GM Mode 0xAE (Device Control)
        test_command(dev, chan_id, "GM Mode 0xAE Device Control (Fan Relay)", 0x7E0, [0x03, 0xAE, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00])

        # 3. Test UDS 0x10 Extended Session on ECM
        test_command(dev, chan_id, "UDS DiagnosticSession 0x03 (Extended)", 0x7E0, [0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])

        # 4. Test GM Security Access Seed Request (0x27 0x01) on ECM
        test_command(dev, chan_id, "UDS SecurityAccess (Request Seed 0x27 0x01)", 0x7E0, [0x02, 0x27, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])

        # 5. Test IPC Cluster on 0x720 vs BCM on 0x7E4
        test_command(dev, chan_id, "Ping Cluster IPC (0x720)", 0x720, [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        test_command(dev, chan_id, "Ping Body Control Module BCM (0x7E4)", 0x7E4, [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # 6. Test Freeze Frame (Mode 02) for P0104
        test_command(dev, chan_id, "OBD Mode 02 PID 02 (Freeze Frame DTC)", 0x7E0, [0x03, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])

    finally:
        dev.disconnect()
        dev.close()
        print("\n[OK] Inspector complete.")

if __name__ == "__main__":
    main()
