7/17/26, 12:52 AM Other CAN Bus Tools \- python-can 4.6.1 documentation **Other CAN Bus Tools**   
In order to keep the project maintainable, the scope of the package is limited to providing common abstractions to different hardware devices, and a basic suite of utilities for sending and receiving messages on a CAN bus. Other tools are available that either extend the functionality of python-can, or provide complementary features that python-can users might find useful. 

Some of these tools are listed below for convenience. 

**CAN Message protocols (implemented in Python)** 

1\. **SAE J1939 Message Protocol** 

The can-j1939 module provides an implementation of the CAN SAE J1939 standard for Python, including J1939-22. can-j1939 uses python-can to provide support for multiple hardware interfaces. 

2\. **CIA CANopen** 

The canopen module provides an implementation of the CIA CANopen protocol, aiming to be used for automation and testing purposes 

3\. **ISO 15765-2 (ISO TP)** 

The can-isotp module provides an implementation of the ISO TP CAN protocol for sending data packets via a CAN transport layer. 

4\. **UDS** 

The python-uds module is a communication protocol agnostic implementation of the Unified Diagnostic Services (UDS) protocol defined in ISO 14229-1, although it does have extensions for performing UDS over CAN utilising the ISO TP protocol. This module has not been updated for some time. 

The uds module is another tool that implements the UDS protocol, although it does have extensions for performing UDS over CAN utilising the ISO TP protocol. This module has not been updated for some time. 

5\. **XCP** 

The pyxcp module implements the Universal Measurement and Calibration Protocol (XCP). The purpose of XCP is to adjust parameters and acquire current values of internal 

Skip to content variables in an ECU. 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/other-tools.html 1/2  
7/17/26, 12:52 AM Other CAN Bus Tools \- python-can 4.6.1 documentation **CAN Frame Parsing tools etc. (implemented in Python)** 

1\. **CAN Message / Database scripting** 

The cantools package provides multiple methods for interacting with can message database files, and using these files to monitor live buses with a command line monitor tool. 

2\. **CAN Message / Log Decoding** 

The canmatrix module provides methods for converting between multiple popular message frame definition file formats (e.g. .DBC files, .KCD files, .ARXML files etc.). The pretty\_j1939 module can be used to post-process CAN logs of J1939 traffic into human readable terminal prints or into a JSON file for consumption elsewhere in your scripts. 

**Other CAN related tools, programs etc.** 

1\. **Micropython CAN class** 

A CAN class is available for the original micropython pyboard, with much of the same functionality as is available with python-can (but with a different API\!). 

2\. **ASAM MDF Files** 

The asammdf module provides many methods for processing ASAM (Association for Standardization of Automation and Measuring Systems) MDF (Measurement Data Format) files. 

**Note** 

See also the available plugins for python-can in Plugin Interface. 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

stable 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise. 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/other-tools.html 2/2