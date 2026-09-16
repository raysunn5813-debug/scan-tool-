"""
TOPDON RLink & J2534 Test Scanner
Runs diagnostics, detects hardware, reads battery voltage, VIN, and live sensor data.
"""

import sys
import time
from j2534_client import J2534Device, get_installed_j2534_devices, ISO15765

def parse_vin(data: bytes) -> str:
    """Parse Mode 09 PID 02 VIN response."""
    try:
        # Look for 0x49 0x02 response header
        idx = -1
        for i in range(len(data) - 1):
            if data[i] == 0x49 and data[i+1] == 0x02:
                idx = i + 3  # Skip service, PID, and count
                break
        if idx != -1 and idx < len(data):
            vin_bytes = data[idx:]
            vin = "".join([chr(b) for b in vin_bytes if 32 <= b <= 126]).strip()
            if len(vin) >= 11:
                return vin
        
        # Fallback raw ASCII extract
        ascii_chars = [chr(b) for b in data if 32 <= b <= 126]
        text = "".join(ascii_chars)
        return text if len(text) >= 11 else f"Raw: {data.hex(' ')}"
    except Exception as e:
        return f"Error parsing VIN: {e}"

def parse_rpm(data: bytes) -> str:
    """Parse Mode 01 PID 0C RPM response."""
    for i in range(len(data) - 1):
        if data[i] == 0x41 and data[i+1] == 0x0C:
            if i + 3 < len(data):
                a = data[i+2]
                b = data[i+3]
                rpm = ((a * 256) + b) / 4.0
                return f"{rpm:.0f} RPM"
    return f"Raw: {data.hex(' ')}"

def parse_coolant(data: bytes) -> str:
    """Parse Mode 01 PID 05 Coolant Temp."""
    for i in range(len(data) - 1):
        if data[i] == 0x41 and data[i+1] == 0x05:
            if i + 2 < len(data):
                celsius = data[i+2] - 40
                fahrenheit = (celsius * 9/5) + 32
                return f"{fahrenheit:.1f} °F ({celsius} °C)"
    return f"Raw: {data.hex(' ')}"

def parse_speed(data: bytes) -> str:
    """Parse Mode 01 PID 0D Vehicle Speed."""
    for i in range(len(data) - 1):
        if data[i] == 0x41 and data[i+1] == 0x0D:
            if i + 2 < len(data):
                kmh = data[i+2]
                mph = kmh * 0.621371
                return f"{mph:.1f} MPH ({kmh} km/h)"
    return f"Raw: {data.hex(' ')}"

def parse_throttle(data: bytes) -> str:
    """Parse Mode 01 PID 11 Throttle Position."""
    for i in range(len(data) - 1):
        if data[i] == 0x41 and data[i+1] == 0x11:
            if i + 2 < len(data):
                pct = (data[i+2] * 100.0) / 255.0
                return f"{pct:.1f}%"
    return f"Raw: {data.hex(' ')}"

def main():
    print("==================================================")
    print("      SUPER SCAN TOOL - TOPDON RLink Test         ")
    print("==================================================")
    
    devices = get_installed_j2534_devices()
    if not devices:
        print("[!] No J2534 devices found in Windows registry.")
        return

    # Select TOPDON 64-bit DLL
    selected_device = None
    for dev in devices:
        if "PassThru464.dll" in dev["dll_path"]:
            selected_device = dev
            break
    if not selected_device:
        selected_device = devices[0]

    print(f"\n[*] Target Hardware: {selected_device['name']}")
    print(f"[*] DLL: {selected_device['dll_path']}")

    try:
        dev = J2534Device(selected_device["dll_path"])
        dev_id = dev.open()
        print(f"[OK] Connected to hardware (Device ID: {dev_id})")
    except Exception as e:
        print(f"[!] Failed to open J2534 device: {e}")
        return

    try:
        vbatt = dev.read_battery_voltage()
        print(f"[OK] OBD-II Pin 16 Battery Voltage: {vbatt:.2f} V")

        print("\n[*] Initializing ISO15765 CAN Channel (500 kbps)...")
        chan_id = dev.connect(protocol_id=ISO15765, baudrate=500000)
        print(f"[OK] CAN Channel opened (ID: {chan_id})")
        
        dev.setup_obd2_filter()
        print("[OK] OBD-II Filter configured successfully.")

        print("\n" + "="*50)
        print("         POLLING VEHICLE ECU DATA")
        print("="*50)

        # 1. VIN Request
        print("\n[>] Requesting VIN (Mode 09 PID 02)...")
        vin_resps = dev.send_obd2_request(service=0x09, pid=0x02, timeout_ms=1500)
        if vin_resps:
            for r in vin_resps:
                print(f"    [+] VIN Detected: {parse_vin(r)}")
        else:
            print("    [-] No VIN response received.")

        # 2. Coolant Temperature
        print("\n[>] Requesting Engine Coolant Temp (Mode 01 PID 05)...")
        coolant_resps = dev.send_obd2_request(service=0x01, pid=0x05, timeout_ms=1000)
        if coolant_resps:
            for r in coolant_resps:
                print(f"    [+] Coolant Temp: {parse_coolant(r)}")
        else:
            print("    [-] No response.")

        # 3. Engine RPM
        print("\n[>] Requesting Engine RPM (Mode 01 PID 0C)...")
        rpm_resps = dev.send_obd2_request(service=0x01, pid=0x0C, timeout_ms=1000)
        if rpm_resps:
            for r in rpm_resps:
                print(f"    [+] Engine Speed: {parse_rpm(r)}")
        else:
            print("    [-] No response.")

        # 4. Vehicle Speed
        print("\n[>] Requesting Vehicle Speed (Mode 01 PID 0D)...")
        speed_resps = dev.send_obd2_request(service=0x01, pid=0x0D, timeout_ms=1000)
        if speed_resps:
            for r in speed_resps:
                print(f"    [+] Vehicle Speed: {parse_speed(r)}")
        else:
            print("    [-] No response.")

        # 5. Throttle Position
        print("\n[>] Requesting Throttle Position (Mode 01 PID 11)...")
        throttle_resps = dev.send_obd2_request(service=0x01, pid=0x11, timeout_ms=1000)
        if throttle_resps:
            for r in throttle_resps:
                print(f"    [+] Throttle Position: {parse_throttle(r)}")
        else:
            print("    [-] No response.")

        print("\n" + "="*50)
        print("          ALL DIAGNOSTIC QUERIES COMPLETE")
        print("="*50)

    except Exception as e:
        print(f"\n[!] Error during scan: {e}")
    finally:
        print("\n[*] Disconnecting CAN channel...")
        dev.disconnect()
        print("[*] Closing J2534 device...")
        dev.close()
        print("[OK] Finished cleanly.")

if __name__ == "__main__":
    main()
