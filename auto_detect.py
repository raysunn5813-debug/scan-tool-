"""
Vehicle Protocol & CAN Bus Auto-Detector
Sniffs raw CAN traffic, detects bus speed (500k vs 250k), tests 11-bit & 29-bit ISO15765.
"""

import sys
import time
import ctypes
from j2534_client import (
    J2534Device, get_installed_j2534_devices, PASSTHRU_MSG,
    CAN, ISO15765, PASS_FILTER, STATUS_NOERROR,
    CLEAR_RX_BUFFER, CLEAR_TX_BUFFER, CLEAR_MSG_FILTERS,
    ISO15765_FRAME_PAD, CAN_29BIT_ID
)

def sniff_raw_can(dev: J2534Device, baudrate: int = 500000, duration_sec: float = 2.0):
    """Listen for any background CAN messages on the bus."""
    print(f"\n[*] Sniffing raw CAN bus at {baudrate//1000} kbps for {duration_sec}s...")
    try:
        chan_id = dev.connect(protocol_id=CAN, baudrate=baudrate)
    except Exception as e:
        print(f"    [-] Could not open raw CAN channel: {e}")
        return False, 0

    try:
        # Pass all messages filter (Mask=0, Pattern=0)
        mask = PASSTHRU_MSG()
        mask.ProtocolID = CAN
        mask.DataSize = 4
        
        pattern = PASSTHRU_MSG()
        pattern.ProtocolID = CAN
        pattern.DataSize = 4

        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))

        start_time = time.time()
        packet_count = 0
        samples = []

        while time.time() - start_time < duration_sec:
            rx_msgs = (PASSTHRU_MSG * 20)()
            rx_count = ctypes.c_ulong(20)
            status = dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 200)
            
            if status == STATUS_NOERROR and rx_count.value > 0:
                packet_count += rx_count.value
                for i in range(rx_count.value):
                    if len(samples) < 5:
                        msg_data = bytes(rx_msgs[i].Data[:rx_msgs[i].DataSize])
                        can_id = int.from_bytes(msg_data[:4], "big")
                        payload = msg_data[4:].hex(' ')
                        samples.append(f"CAN ID: 0x{can_id:03X} | Data: {payload}")

        if packet_count > 0:
            print(f"    [+] ACTIVE BUS DETECTED! Captured {packet_count} CAN frames.")
            for s in samples:
                print(f"        -> {s}")
            return True, packet_count
        else:
            print(f"    [-] No CAN frames captured at {baudrate//1000} kbps.")
            return False, 0

    finally:
        dev.disconnect()

def test_iso15765(dev: J2534Device, baudrate: int, is_29bit: bool):
    """Test standard Mode 01 PID 00 query."""
    mode_name = f"{'29-bit' if is_29bit else '11-bit'} CAN @ {baudrate//1000}k"
    print(f"\n[*] Testing OBD-II ({mode_name})...")
    
    flags = CAN_29BIT_ID if is_29bit else 0
    try:
        chan_id = dev.connect(protocol_id=ISO15765, baudrate=baudrate, flags=flags)
    except Exception as e:
        print(f"    [-] Connect failed: {e}")
        return None

    try:
        # Pass-all filter on ISO15765
        dev.dll.PassThruIoctl(chan_id, CLEAR_MSG_FILTERS, None, None)
        mask = PASSTHRU_MSG()
        mask.ProtocolID = ISO15765
        mask.DataSize = 4
        
        pattern = PASSTHRU_MSG()
        pattern.ProtocolID = ISO15765
        pattern.DataSize = 4

        filter_id = ctypes.c_ulong(0)
        dev.dll.PassThruStartMsgFilter(chan_id, PASS_FILTER, ctypes.byref(mask), ctypes.byref(pattern), None, ctypes.byref(filter_id))

        # Build request message
        msg = PASSTHRU_MSG()
        msg.ProtocolID = ISO15765
        msg.TxFlags = ISO15765_FRAME_PAD | (CAN_29BIT_ID if is_29bit else 0)
        
        if is_29bit:
            # 29-bit Broadcast: 0x18DB33F1
            msg.DataSize = 6
            msg.Data[0] = 0x18
            msg.Data[1] = 0xDB
            msg.Data[2] = 0x33
            msg.Data[3] = 0xF1
            msg.Data[4] = 0x01  # Mode 01
            msg.Data[5] = 0x00  # PID 00
        else:
            # 11-bit Broadcast: 0x7DF
            msg.DataSize = 6
            msg.Data[0] = 0x00
            msg.Data[1] = 0x00
            msg.Data[2] = 0x07
            msg.Data[3] = 0xDF
            msg.Data[4] = 0x01  # Mode 01
            msg.Data[5] = 0x00  # PID 00

        dev.dll.PassThruIoctl(chan_id, CLEAR_RX_BUFFER, None, None)
        dev.dll.PassThruIoctl(chan_id, CLEAR_TX_BUFFER, None, None)

        num_msgs = ctypes.c_ulong(1)
        dev.dll.PassThruWriteMsgs(chan_id, ctypes.byref(msg), ctypes.byref(num_msgs), 1000)

        # Listen for reply
        rx_msgs = (PASSTHRU_MSG * 10)()
        rx_count = ctypes.c_ulong(10)
        time.sleep(0.1)
        status = dev.dll.PassThruReadMsgs(chan_id, rx_msgs, ctypes.byref(rx_count), 1000)

        if status == STATUS_NOERROR and rx_count.value > 0:
            print(f"    [SUCCESS] Received {rx_count.value} response(s)!")
            for i in range(rx_count.value):
                resp = bytes(rx_msgs[i].Data[:rx_msgs[i].DataSize])
                print(f"        Raw: {resp.hex(' ')}")
            return True
        else:
            print("    [-] No response from ECU.")
            return False

    finally:
        dev.disconnect()

def main():
    print("==================================================")
    print("      VEHICLE PROTOCOL & BUS AUTO-DETECTOR        ")
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
        print(f"[OK] Pin 16 Voltage: {vbatt:.2f} V (Engine Running)")

        # Step 1: Sniff raw CAN at 500k and 250k
        active_500k, _ = sniff_raw_can(dev, baudrate=500000, duration_sec=2.0)
        active_250k, _ = sniff_raw_can(dev, baudrate=250000, duration_sec=2.0)

        # Step 2: Test OBD queries
        print("\n" + "="*50)
        print("          TESTING OBD-II PROTOCOL MODES")
        print("="*50)
        
        # Test 11-bit 500k
        test_iso15765(dev, baudrate=500000, is_29bit=False)
        
        # Test 29-bit 500k
        test_iso15765(dev, baudrate=500000, is_29bit=True)

        # Test 11-bit 250k
        test_iso15765(dev, baudrate=250000, is_29bit=False)

        # Test 29-bit 250k
        test_iso15765(dev, baudrate=250000, is_29bit=True)

    finally:
        dev.close()
        print("\n[OK] Scan completed.")

if __name__ == "__main__":
    main()
