7/17/26, 12:51 AM Multicast IP Interface \- python-can 4.6.1 documentation **Multicast IP Interface**   
This module implements transport of CAN and CAN FD messages over UDP via Multicast IPv4 and IPv6. This virtual interface allows for communication between multiple processes and even hosts. This differentiates it from the Virtual interface, which can only passes messages within a single process but does not require a network stack. 

It runs on UDP to have the lowest possible latency (as opposed to using TCP), and because normal IP multicast is inherently unreliable, as the recipients are unknown. This enables ad-hoc networks that do not require a central server but is also a so-called *unreliable network*. In practice however, local area networks (LANs) should most often be sufficiently reliable for this interface to function properly. 

**Note** 

For an overview over the different virtual buses in this library and beyond, please refer to the section Virtual Interfaces. It also describes important limitations of this interface. 

Please refer to the Bus class documentation below for configuration options and useful resources for specifying multicast IP addresses. 

**Installation** 

The Multicast IP Interface depends on the **msgpack** python library, which is automatically installed with the *multicast* extra keyword: 

$ pip install python-can\[multicast\] 

**Supported Platforms** 

It should work on most Unix systems (including Linux with kernel 2.6.22+ and macOS) but currently not on Windows. 

**Example** 

This example should print a single line indicating that a CAN message was successfully sent from bus\_1 to bus\_2 :   
Skip to content 

**10,000 free credits to start** Sign up with Google and make your first call in minutes. **Get a key →** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/interfaces/udp\_multicast.html 1/6  
7/17/26, 12:51 AM Multicast IP Interface \- python-can 4.6.1 documentation 

**import time** 

**import can** 

**from can.interfaces.udp\_multicast import** UdpMulticastBus 

*\# The bus can be created using the can.Bus wrapper class or using UdpMulticastBus directly* **with** can.Bus(channel\=UdpMulticastBus.DEFAULT\_GROUP\_IPv6, interface\='udp\_multicast') **as** bus\_1, \\  UdpMulticastBus(channel\=UdpMulticastBus.DEFAULT\_GROUP\_IPv6) **as** bus\_2: 

 *\# register a callback on the second bus that prints messages to the standard out*  notifier \= can.Notifier(bus\_2, \[can.Printer()\]) 

 *\# create and send a message with the first bus, which should arrive at the second one*  message \= can.Message(arbitration\_id\=0x123, data\=\[1, 2, 3\]) 

 bus\_1.send(message) 

 *\# give the notifier enough time to get triggered by the second bus* 

 time.sleep(2.0) 

 *\# clean-up* 

 notifier.stop() 

Skip to content 

**10,000 free credits to start** Sign up with Google and make your first call in minutes. **Get a key →** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/interfaces/udp\_multicast.html 2/6  
7/17/26, 12:51 AM Multicast IP Interface \- python-can 4.6.1 documentation **Bus Class Documentation** 

**class** 

can.interfaces.udp\_multicast.**UdpMulticastBus(channel='ff15:7079:7468:6f6e:6465:6d6f:6d 63:6173', port=43113, hop\_limit=1, receive\_own\_messages=False, fd=True, \*\*kwargs)** 

A virtual interface for CAN communications between multiple processes using UDP over Multicast IP.   
\[source\] 

It supports IPv4 and IPv6, specified via the channel (which really is just a multicast IP address as a string). You can also specify the port and the IPv6 *hop limit*/the IPv4 *time to live* (TTL). 

This bus does not support filtering based on message IDs on the kernel level but instead provides it in user space (in Python) as a fallback. 

Both default addresses should allow for multi-host CAN networks in a normal local area network (LAN) where multicast is enabled. 

**Note** 

The auto-detection of available interfaces (see) is implemented using heuristic that checks if the required socket operations are available. It then returns two configurations, one based on the DEFAULT\_GROUP\_IPv6 address and another one based on the DEFAULT\_GROUP\_IPv4 address. 

**Warning** 

The parameter *receive\_own\_messages* is currently unsupported and setting it to *True* will raise an exception. 

Skip to content 

**10,000 free credits to start** Sign up with Google and make your first call in minutes. **Get a key →** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/interfaces/udp\_multicast.html 3/6  
7/17/26, 12:51 AM Multicast IP Interface \- python-can 4.6.1 documentation **Warning** 

This interface does not make guarantees on reliable delivery and message ordering, and also does not implement rate limiting or ID arbitration/prioritization under high loads. Please refer to the section Virtual Interfaces for more information on this and a comparison to alternatives. 

**PARAMETERS:** 

**channel** (*str*) – A multicast IPv4 address (in *224.0.0.0/4*) or an IPv6 address (in *ff00::/8*). This defines which version of IP is used. See Wikipedia (“Multicast address”) for more details on the addressing schemes. Defaults to DEFAULT\_GROUP\_IPv6 . 

**port** (*int*) – The IP port to read from and write to. 

**hop\_limit** (*int*) – The hop limit in IPv6 or in IPv4 the time to live (TTL). 

**receive\_own\_messages** (*bool*) – If transmitted messages should also be received by this bus. CURRENTLY UNSUPPORTED. 

**fd** (*bool*) – If CAN-FD frames should be supported. If set to false, an error will be raised upon sending such a frame and such received frames will be ignored. 

**can\_filters** – See set\_filters() . 

**kwargs** (*Any*) 

**RAISES:** 

**RuntimeError** – If the *msgpack*\-dependency is not available. It should be installed on all non Windows platforms via the *setup.py* requirements. 

**NotImplementedError** – If the *receive\_own\_messages* is passed as *True*. 

Construct and open a CAN bus instance of the specified type. 

Skip to content 

**10,000 free credits to start** Sign up with Google and make your first call in minutes. **Get a key →** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/interfaces/udp\_multicast.html 4/6  
7/17/26, 12:51 AM Multicast IP Interface \- python-can 4.6.1 documentation Subclasses should call though this method with all given parameters as it handles generic tasks like applying filters. 

**PARAMETERS:** 

**channel** (*str*) – The can interface identifier. Expected type is backend dependent. **can\_filters** – See set\_filters() for details. 

**kwargs** (*dict*) – Any backend dependent configurations are passed in this dictionary **port** (*int*) 

**hop\_limit** (*int*) 

**receive\_own\_messages** (*bool*) 

**fd** (*bool*) 

**RAISES:** 

**ValueError** – If parameters are out of range 

**CanInterfaceNotImplementedError** – If the driver cannot be accessed 

**CanInitializationError** – If the bus cannot be initialized 

**DEFAULT\_GROUP\_IPv4 \= '239.74.163.2'** 

An arbitrary IPv4 multicast address with “administrative” scope, i.e. only to be routed within administrative organizational boundaries and not beyond it. It should allow for multi-host CAN networks in a normal IPv4 LAN. This is provided as a default fallback channel if IPv6 is (still) not supported. 

**DEFAULT\_GROUP\_IPv6 \= 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'** 

An arbitrary IPv6 multicast address with “site-local” scope, i.e. only to be routed within the local physical network and not beyond it. It should allow for multi-host CAN networks in a normal IPv6 LAN. This is the default channel and should work with most modern routers if multicast is allowed. 

**fileno()** 

Provides the internally used file descriptor of the socket or *\-1* if not available. 

**RETURN TYPE:** 

int 

**shutdown()** 

Close all sockets and free up any resources. 

Never throws errors and only logs them. 

Skip to content   
**RETURN TYPE:**   
\[source\] 

\[source\] 

stable 

**10,000 free credits to start** Sign up with Google and make your first call in minutes. 

*Ads by* 

**Get a key →**   
None 

*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/interfaces/udp\_multicast.html 5/6  
7/17/26, 12:51 AM Multicast IP Interface \- python-can 4.6.1 documentation 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

**10,000 free credits to start** Sign up with Google and make your first call in minutes. **Get a key →** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/interfaces/udp\_multicast.html 6/6