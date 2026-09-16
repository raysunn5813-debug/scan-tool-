"""
Standalone J2534 Python Client using ctypes
Directly interfaces with J2534 v04.04 DLLs (TOPDON RLink, Tactrix, Mongoose, etc.).
"""

import ctypes
import winreg
import struct
import time
from typing import List, Dict, Optional, Tuple

# SAE J2534-1 Official Protocol IDs
J1850VPW       = 0x01
J1850PWM       = 0x02
ISO9141        = 0x03
ISO14230       = 0x04
CAN            = 0x05
ISO15765       = 0x06
SCI_A_ENGINE   = 0x07
SCI_A_TRANS    = 0x08
SCI_B_ENGINE   = 0x09
SCI_B_TRANS    = 0x0A

# Filter Types
PASS_FILTER         = 0x00000001
BLOCK_FILTER        = 0x00000002
FLOW_CONTROL_FILTER = 0x00000003

# Tx / Rx Flags
ISO15765_FRAME_PAD = 0x00000040
ISO15765_ADDR_TYPE = 0x00000080
CAN_29BIT_ID       = 0x00000100
WAIT_P3_MIN_ONLY   = 0x00000200
CAN_ID_BOTH        = 0x00000800

# IOCTL IDs
GET_CONFIG                   = 0x01
SET_CONFIG                   = 0x02
READ_VBATT                   = 0x03
FIVE_BAUD_INIT               = 0x04
FAST_INIT                    = 0x05
CLEAR_TX_BUFFER              = 0x07
CLEAR_RX_BUFFER              = 0x08
CLEAR_PERIODIC_MSGS          = 0x09
CLEAR_MSG_FILTERS            = 0x0A
CLEAR_FUNCT_MSG_LOOKUP_TABLE = 0x0B
ADD_TO_FUNCT_MSG_LOOKUP_TABLE= 0x0C
DELETE_FROM_FUNCT_MSG_LOOKUP_TABLE = 0x0D
READ_PROG_VOLTAGE            = 0x0E

# Error Codes
STATUS_NOERROR              = 0x00
ERR_NOT_SUPPORTED           = 0x01
ERR_INVALID_CHANNEL_ID      = 0x02
ERR_INVALID_PROTOCOL_ID     = 0x03
ERR_NULLPARAMETER           = 0x04
ERR_INVALID_IOCTL_VALUE     = 0x05
ERR_INVALID_FLAGS           = 0x06
ERR_FAILED                  = 0x07
ERR_DEVICE_NOT_CONNECTED    = 0x08
ERR_TIMEOUT                 = 0x09
ERR_INVALID_MSG             = 0x0A
ERR_EXCEEDED_LIMIT          = 0x0B
ERR_INVALID_MSG_ID          = 0x0C
ERR_DEVICE_IN_USE           = 0x0D
ERR_INVALID_IOCTL_ID        = 0x0E
ERR_BUFFER_EMPTY            = 0x0F
ERR_BUFFER_FULL             = 0x10
ERR_BUFFER_OVERFLOW         = 0x11
ERR_PIN_INVALID             = 0x12
ERR_CHANNEL_IN_USE          = 0x13
ERR_MSG_PROTOCOL_ID         = 0x14
ERR_INVALID_FILTER_ID       = 0x15
ERR_NO_FLOW_CONTROL         = 0x16
ERR_NOT_UNIQUE              = 0x17
ERR_UNRECOGNIZED_FLAG       = 0x18
ERR_NULL_CALLBACK           = 0x19

ERROR_NAMES = {
    0x00: "STATUS_NOERROR",
    0x01: "ERR_NOT_SUPPORTED",
    0x02: "ERR_INVALID_CHANNEL_ID",
    0x03: "ERR_INVALID_PROTOCOL_ID",
    0x04: "ERR_NULLPARAMETER",
    0x05: "ERR_INVALID_IOCTL_VALUE",
    0x06: "ERR_INVALID_FLAGS",
    0x07: "ERR_FAILED",
    0x08: "ERR_DEVICE_NOT_CONNECTED",
    0x09: "ERR_TIMEOUT",
    0x0A: "ERR_INVALID_MSG",
    0x0B: "ERR_EXCEEDED_LIMIT",
    0x0C: "ERR_INVALID_MSG_ID",
    0x0D: "ERR_DEVICE_IN_USE",
    0x0E: "ERR_INVALID_IOCTL_ID",
    0x0F: "ERR_BUFFER_EMPTY",
    0x10: "ERR_BUFFER_FULL",
    0x11: "ERR_BUFFER_OVERFLOW",
    0x12: "ERR_PIN_INVALID",
    0x13: "ERR_CHANNEL_IN_USE",
    0x14: "ERR_MSG_PROTOCOL_ID",
    0x15: "ERR_INVALID_FILTER_ID",
    0x16: "ERR_NO_FLOW_CONTROL",
    0x17: "ERR_NOT_UNIQUE",
    0x18: "ERR_UNRECOGNIZED_FLAG",
    0x19: "ERR_NULL_CALLBACK"
}

# Structures
class PASSTHRU_MSG(ctypes.Structure):
    _fields_ = [
        ("ProtocolID", ctypes.c_ulong),
        ("RxStatus", ctypes.c_ulong),
        ("TxFlags", ctypes.c_ulong),
        ("Timestamp", ctypes.c_ulong),
        ("DataSize", ctypes.c_ulong),
        ("ExtraDataIndex", ctypes.c_ulong),
        ("Data", ctypes.c_ubyte * 4128)
    ]

def get_installed_j2534_devices() -> List[Dict[str, str]]:
    """Scan Windows Registry for installed J2534 devices."""
    devices = []
    
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\PassThruSupport.04.04"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\PassThruSupport.04.04")
    ]
    
    for root_key, sub_key in reg_paths:
        try:
            with winreg.OpenKey(root_key, sub_key) as key:
                num_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(num_subkeys):
                    device_key_name = winreg.EnumKey(key, i)
                    try:
                        with winreg.OpenKey(key, device_key_name) as dev_key:
                            name, _ = winreg.QueryValueEx(dev_key, "Name")
                            dll_path, _ = winreg.QueryValueEx(dev_key, "FunctionLibrary")
                            vendor = ""
                            try:
                                vendor, _ = winreg.QueryValueEx(dev_key, "Vendor")
                            except FileNotFoundError:
                                pass
                            
                            devices.append({
                                "name": name,
                                "vendor": vendor,
                                "dll_path": dll_path,
                                "reg_key": device_key_name
                            })
                    except Exception:
                        continue
        except FileNotFoundError:
            continue

    unique = []
    seen = set()
    for d in devices:
        if d["dll_path"] not in seen:
            seen.add(d["dll_path"])
            unique.append(d)
    return unique


class J2534Device:
    def __init__(self, dll_path: str):
        self.dll_path = dll_path
        self.dll = ctypes.WinDLL(dll_path)
        self.device_id = ctypes.c_ulong(0)
        self.channel_id = ctypes.c_ulong(0)
        self.filter_ids = []
        self._setup_prototypes()

    def _setup_prototypes(self):
        self.dll.PassThruOpen.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        self.dll.PassThruOpen.restype = ctypes.c_long

        self.dll.PassThruClose.argtypes = [ctypes.c_ulong]
        self.dll.PassThruClose.restype = ctypes.c_long

        self.dll.PassThruConnect.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
        self.dll.PassThruConnect.restype = ctypes.c_long

        self.dll.PassThruDisconnect.argtypes = [ctypes.c_ulong]
        self.dll.PassThruDisconnect.restype = ctypes.c_long

        self.dll.PassThruStartMsgFilter.argtypes = [
            ctypes.c_ulong, ctypes.c_ulong,
            ctypes.POINTER(PASSTHRU_MSG),
            ctypes.POINTER(PASSTHRU_MSG),
            ctypes.POINTER(PASSTHRU_MSG),
            ctypes.POINTER(ctypes.c_ulong)
        ]
        self.dll.PassThruStartMsgFilter.restype = ctypes.c_long

        self.dll.PassThruStopMsgFilter.argtypes = [ctypes.c_ulong, ctypes.c_ulong]
        self.dll.PassThruStopMsgFilter.restype = ctypes.c_long

        self.dll.PassThruWriteMsgs.argtypes = [ctypes.c_ulong, ctypes.POINTER(PASSTHRU_MSG), ctypes.POINTER(ctypes.c_ulong), ctypes.c_ulong]
        self.dll.PassThruWriteMsgs.restype = ctypes.c_long

        self.dll.PassThruReadMsgs.argtypes = [ctypes.c_ulong, ctypes.POINTER(PASSTHRU_MSG), ctypes.POINTER(ctypes.c_ulong), ctypes.c_ulong]
        self.dll.PassThruReadMsgs.restype = ctypes.c_long

        self.dll.PassThruIoctl.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]
        self.dll.PassThruIoctl.restype = ctypes.c_long

        self.dll.PassThruGetLastError.argtypes = [ctypes.c_char_p]
        self.dll.PassThruGetLastError.restype = ctypes.c_long

    def get_last_error(self) -> str:
        buf = ctypes.create_string_buffer(512)
        self.dll.PassThruGetLastError(buf)
        return buf.value.decode("utf-8", errors="ignore")

    def _check_status(self, status: int, action: str):
        if status != STATUS_NOERROR:
            err_name = ERROR_NAMES.get(status, f"UNKNOWN_ERROR (0x{status:02X})")
            extra = self.get_last_error()
            raise RuntimeError(f"Failed to {action}: {err_name} ({extra})")

    def open(self):
        """Open connection to the physical J2534 hardware interface."""
        status = self.dll.PassThruOpen(None, ctypes.byref(self.device_id))
        self._check_status(status, "PassThruOpen")
        return self.device_id.value

    def close(self):
        """Close connection to the hardware."""
        if self.device_id.value != 0:
            self.dll.PassThruClose(self.device_id)
            self.device_id = ctypes.c_ulong(0)

    def read_battery_voltage(self) -> float:
        """Read vehicle battery voltage in Volts."""
        vbatt_mv = ctypes.c_ulong(0)
        status = self.dll.PassThruIoctl(self.device_id, READ_VBATT, None, ctypes.byref(vbatt_mv))
        if status == STATUS_NOERROR:
            return vbatt_mv.value / 1000.0
        return 0.0

    def connect(self, protocol_id=ISO15765, baudrate=500000, flags=0):
        """Open communication channel to vehicle network (default: ISO15765 CAN 500k)."""
        status = self.dll.PassThruConnect(self.device_id, protocol_id, flags, baudrate, ctypes.byref(self.channel_id))
        self._check_status(status, f"PassThruConnect (Protocol {protocol_id})")
        return self.channel_id.value

    def disconnect(self):
        """Disconnect communication channel."""
        if self.channel_id.value != 0:
            self.dll.PassThruDisconnect(self.channel_id)
            self.channel_id = ctypes.c_ulong(0)

    def setup_obd2_filter(self):
        """Set up standard ISO15765 CAN flow control & pass filters for OBD2."""
        self.dll.PassThruIoctl(self.channel_id, CLEAR_MSG_FILTERS, None, None)
        self.filter_ids = []

        # 11-bit ISO15765 Flow Control Filter (0x7E8 - 0x7EF)
        mask_msg = PASSTHRU_MSG()
        mask_msg.ProtocolID = ISO15765
        mask_msg.TxFlags = 0
        mask_msg.DataSize = 4
        mask_msg.Data[0] = 0x00
        mask_msg.Data[1] = 0x00
        mask_msg.Data[2] = 0x07
        mask_msg.Data[3] = 0xF8  # Matches 0x7E8 to 0x7EF

        pattern_msg = PASSTHRU_MSG()
        pattern_msg.ProtocolID = ISO15765
        pattern_msg.TxFlags = 0
        pattern_msg.DataSize = 4
        pattern_msg.Data[0] = 0x00
        pattern_msg.Data[1] = 0x00
        pattern_msg.Data[2] = 0x07
        pattern_msg.Data[3] = 0xE8

        flow_msg = PASSTHRU_MSG()
        flow_msg.ProtocolID = ISO15765
        flow_msg.TxFlags = 0
        flow_msg.DataSize = 4
        flow_msg.Data[0] = 0x00
        flow_msg.Data[1] = 0x00
        flow_msg.Data[2] = 0x07
        flow_msg.Data[3] = 0xE0

        filter_id = ctypes.c_ulong(0)
        status = self.dll.PassThruStartMsgFilter(
            self.channel_id,
            FLOW_CONTROL_FILTER,
            ctypes.byref(mask_msg),
            ctypes.byref(pattern_msg),
            ctypes.byref(flow_msg),
            ctypes.byref(filter_id)
        )

        if status == STATUS_NOERROR:
            self.filter_ids.append(filter_id.value)
        else:
            # Fallback to PASS_FILTER
            status = self.dll.PassThruStartMsgFilter(
                self.channel_id,
                PASS_FILTER,
                ctypes.byref(mask_msg),
                ctypes.byref(pattern_msg),
                None,
                ctypes.byref(filter_id)
            )
            if status == STATUS_NOERROR:
                self.filter_ids.append(filter_id.value)

        return self.filter_ids

    def send_obd2_request(self, service: int, pid: int, timeout_ms: int = 1500) -> List[bytes]:
        """
        Send a standard OBD2 request (e.g. Service 01 PID 0C for RPM).
        Returns list of response data bytes from responding ECU(s).
        """
        self.dll.PassThruIoctl(self.channel_id, CLEAR_RX_BUFFER, None, None)
        self.dll.PassThruIoctl(self.channel_id, CLEAR_TX_BUFFER, None, None)

        msg = PASSTHRU_MSG()
        msg.ProtocolID = ISO15765
        msg.TxFlags = ISO15765_FRAME_PAD
        msg.DataSize = 6  # 4 bytes CAN ID (0x000007DF) + 2 bytes [service, pid]
        msg.ExtraDataIndex = 0
        
        # 11-bit CAN Broadcast ID 0x7DF
        msg.Data[0] = 0x00
        msg.Data[1] = 0x00
        msg.Data[2] = 0x07
        msg.Data[3] = 0xDF
        # OBD Payload
        msg.Data[4] = service
        msg.Data[5] = pid

        num_msgs = ctypes.c_ulong(1)
        status = self.dll.PassThruWriteMsgs(self.channel_id, ctypes.byref(msg), ctypes.byref(num_msgs), timeout_ms)
        self._check_status(status, "PassThruWriteMsgs")

        # Read response
        rx_msgs = (PASSTHRU_MSG * 10)()
        rx_count = ctypes.c_ulong(10)
        
        time.sleep(0.08)
        status = self.dll.PassThruReadMsgs(self.channel_id, rx_msgs, ctypes.byref(rx_count), timeout_ms)
        
        responses = []
        if status == STATUS_NOERROR and rx_count.value > 0:
            for i in range(rx_count.value):
                raw = bytes(rx_msgs[i].Data[:rx_msgs[i].DataSize])
                responses.append(raw)
        return responses
