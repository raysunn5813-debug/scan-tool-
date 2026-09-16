"""
Direct CAN Bus OBD-II Diagnostic Scanner
Uses Raw CAN Protocol (0x05) at 500kbps to send and receive standard OBD-II and UDS queries.
"""

import sys
import time
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, PASS_FILTER, STATUS_NOERROR, CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS
)

def build_can_msg(can_id: int, payload: bytes) -> PASSTHRU_MSG:
    """Construct an 8-byte CAN frame with 4-byte CAN ID header."""
    msg = PASSTHRU_MSG()
    msg.ProtocolID = CAN
    msg.TxFlags = 0
    msg.DataSize = 4 + len(payload)
    
    # 4-byte CAN ID header (Big-Endian)
    msg.Data[0] = (can_id >> 24) & 0xFF
    msg.Data[1] = (can_id >> 16) & 0xFF
    msg.Data[2] = (can_id >> 8) & 0xFF
    msg.Data[3] = can_id & 0xFF
    
    # Payload bytes
    for i, b in enumerate(payload):
        msg.Data[4 + i] = b
    return msg

def parse_can_msg(msg: PASSTHRU_MSG):
    data = bytes(msg.Data[:msg.DataSize])
    if len(data) < 4:
        return None, b""
    can_id = int.from_bytes(data[:4], "big")
    payload = data[4:]
    return can_id, payload

def send_query_and_listen(dev: J2534Device, chan_id: int, target_id: int, service: int, pid: int = None, timeout_sec: float = 0.3):
    """
    Send an OBD-II request over raw CAN:
    Format: [Length, Service, PID, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC]
    """
    if pid is not None:
        payload = bytes([0x02, service, pid, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC])
    else:
        payload = bytes([0x01, service, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC])

    tx_msg = build_can_msg(target_id, payload)
    
    # Clear buffers
    dev.dll.PassThruIoctl(chan_id, CLEAR_RX_BUFFER, None, None)
    dev.dll.PassThruIoctl(chan_id, CLEAR_TX_BUFFER, None, None)

    # Transmit
    num_msgs = ctypes.c_ulong(1)
    dev.dll.PassThruWriteMsgs(chan_id, ctypes.byref(tx_msg), ctypes.byref(num_msgs), 500)

    # Listen for response (0x7E8 to 0x7EF, or target_id + 8)
    expected_resp_service = service + 0x40
    start_time = time.time()
    responses = []

    while time.time() - start_time < timeout_sec:
        rx_msgs = (PASSTHRU_MSG * 20)()
        rx_count = ctypes.c_ulong(20)
        status = dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 50)
        
        if status == STATUS_NOERROR and rx_count.value > 0:
            for i in range(rx_count.value):
                can_id, rx_payload = parse_can_msg(rx_msgs[i])
                # Check if it's an OBD response
                if len(rx_payload) >= 2:
                    # Single-frame OBD response: rx_payload[0]=length, rx_payload[1]=service+0x40
                    if rx_payload[1] == expected_resp_service:
                        responses.append((can_id, rx_payload))
                    elif rx_payload[0] == expected_resp_service:
                        responses.append((can_id, rx_payload))
        if responses:
            break
        time.sleep(0.01)

    return responses

def decode_obd_response(can_id: int, payload: bytes):
    """Decode standard OBD Mode 01 & 09 responses."""
    # Find service response byte (0x41 for Mode 01, 0x49 for Mode 09)
    idx = -1
    for i in range(len(payload) - 1):
        if payload[i] in (0x41, 0x49):
            idx = i
            break
    if idx == -1:
        return f"Raw: {payload.hex(' ')}"

    service = payload[idx]
    pid = payload[idx + 1] if idx + 1 < len(payload) else None
    data = payload[idx + 2:]

    if service == 0x41:  # Mode 01 Live Data
        if pid == 0x0C and len(data) >= 2:  # Engine RPM
            rpm = ((data[0] * 256) + data[1]) / 4.0
            return f"Engine RPM: {rpm:.0f} RPM"
        elif pid == 0x05 and len(data) >= 1:  # Coolant Temp
            c = data[0] - 40
            f = (c * 9/5) + 32
            return f"Coolant Temp: {f:.1f} °F ({c} °C)"
        elif pid == 0x0D and len(data) >= 1:  # Vehicle Speed
            kmh = data[0]
            mph = kmh * 0.621371
            return f"Vehicle Speed: {mph:.1f} MPH ({kmh} km/h)"
        elif pid == 0x11 and len(data) >= 1:  # Throttle
            pct = (data[0] * 100.0) / 255.0
            return f"Throttle Position: {pct:.1f}%"
        elif pid == 0x00 and len(data) >= 4:  # Supported PIDs
            return f"Supported PIDs (01-20): 0x{data[:4].hex().upper()}"
        else:
            return f"PID 0x{pid:02X} -> Data: {data.hex(' ')}"

    elif service == 0x49:  # Mode 09 Vehicle Info
        ascii_text = "".join([chr(b) for b in data if 32 <= b <= 126])
        return f"Vehicle Info (PID 0x{pid:02X}): {ascii_text} (Raw: {data.hex(' ')})"

    return f"Response from 0x{can_id:03X}: {payload.hex(' ')}"

def main():
    print("==================================================")
    print("      DIRECT CAN OBD-II LIVE SCANNER              ")
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

        print("[*] Opening CAN Channel at 500 kbps...")
        chan_id = dev.connect(protocol_id=CAN, baudrate=500000)
        print(f"[OK] Channel opened (ID: {chan_id})")

        # Set up filter to catch all diagnostic response IDs (0x7E8 - 0x7EF, 0x700 - 0x7FF)
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        
        mask = build_can_msg(0x00000700, b"")
        pattern = build_can_msg(0x00000700, b"")
        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))
        print("[OK] Diagnostic CAN filter (0x700-0x7FF) active.\n")

        # Test both Broadcast (0x7DF) and Direct PCM Physical Request (0x7E0)
        target_ids = [0x7DF, 0x7E0, 0x7E1, 0x720]
        
        print("="*50)
        print("        QUERYING LIVE SENSOR DATA")
        print("="*50)

        # Queries to run: (Service, PID, Name)
        queries = [
            (0x01, 0x00, "Supported PIDs"),
            (0x01, 0x0C, "Engine RPM"),
            (0x01, 0x05, "Engine Coolant Temp"),
            (0x01, 0x0D, "Vehicle Speed"),
            (0x01, 0x11, "Throttle Position"),
            (0x09, 0x02, "VIN Request")
        ]

        for svc, pid, name in queries:
            print(f"\n[>] Querying {name} (Mode {svc:02X} PID {pid:02X})...")
            found = False
            for target_id in target_ids:
                resps = send_query_and_listen(dev, chan_id, target_id, svc, pid, timeout_sec=0.25)
                if resps:
                    for can_id, payload in resps:
                        decoded = decode_obd_response(can_id, payload)
                        print(f"    [+] [ECU 0x{can_id:03X} (via 0x{target_id:03X})]: {decoded}")
                        found = True
                    break
            if not found:
                print(f"    [-] No response from ECU.")

        print("\n" + "="*50)
        print("           SCAN COMPLETED SUCCESSFULLY")
        print("="*50)

    finally:
        dev.disconnect()
        dev.close()
        print("\n[OK] Device closed cleanly.")

if __name__ == "__main__":
    main()
