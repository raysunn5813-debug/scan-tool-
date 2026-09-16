Docs » **python-can-csscan-serial** overview 

**python-can-csscan-serial** overview 

The Python package **python-can-csscan-serial** adds the CSS Electronics USB-interface to **python-can**. 

The **python-can** library provides CAN-bus support for Python. It comes with a range of tools (similar to Linux *can-utils*) and provides an easy-to-use API for sending and receiving messages over CAN-buses and for working with CAN-bus log-files. 

For more information on **python-can**, see https://python-can.readthedocs.io/en/v4.5.0/. At the time of writing, the current stable version of **python-can** is 4.5.0. 

The **python-can** project only implements basic CAN-bus support. Several projects extend this functionality, adding support for e.g. *J1939*, *CANopen*, *ISO-TP*, *UDS*, *XCP*, and more. For a list of some extensions, see https://python-can.readthedocs.io/en/v4.5.0/other-tools.html. 

Installation 

The **python-can-csscan-serial** package is installed from PyPi with pip. **$** pip install python-can-csscan-serial

Virtual-serial-port 

The USB-interface is listed as a USB *virtual-serial-port*. 

 **Note** 

Only one process can claim access to a serial-port device at a time. It is, however, possible to establish parallel connections to multiple separate serial-ports. 

Windows   
Under Windows, the serial-port can be found in Device Manager \> Ports (COM & LPT) , where it will be named USB Serial Device (e.g USB Serial Device (COM19) ). 

Linux 

Under Linux, the serial-port can be found in /dev/tty\* or by inspecting the journal while connecting the device. 

*Using journalctl for detecting USB serial-port* 

**$** journalctl \-f 

kernel: usb 3-8: New USB device found, idVendor=04d8, idProduct=eb18, bcdDevice= 0.03 kernel: usb 3-8: Product: CANmod 

kernel: usb 3-8: Manufacturer: CSS Electronics 

kernel: cdc\_acm 3-8:1.1: ttyACM0: USB ACM device