7/17/26, 12:50 AM Virtual Interfaces \- python-can 4.6.1 documentation **Virtual Interfaces**   
There are quite a few implementations for CAN networks that do not require physical CAN hardware. The built in virtual interfaces are: 

Virtual 

Multicast IP Interface 

**Comparison** 

The following table compares some known virtual interfaces: 

**Applicability Implementation** 

**Name** 

| Availability | Within  Process | Between  Processes | Via (IP)  Networks | Without Central  Server | Transport  Technology |
| ----- | ----- | ----- | ----- | :---- | ----- |
| *included*  | ✓  | ✗  | ✗  | ✓ | Singleton & Mutex  (reliable) |
| *included*  | ✓  | ✓  | ✓  | ✓ | UDP via IP  multicast  (unreliable) |
| external  | ✓  | ✓  | ✓  | ✗ | Websockets via TCP/IP  (reliable) |
| external  | ✓  | ✓  | ✓  | ✗ | ZeroMQ via TCP/IP  (reliable) |

**Ser** 

**For** 

virtual (this) non 

udp\_multicast 

(doc) 

*christiansandberg/ python-can* 

*remote* 

*windelbouwman/ virtualcan*   
cus usin msg 

cus bina 

cus bina 

    

**\[1\]**   
The only option in this list that implements interoperability with other languages out of the box. For the others (except the first intra-process one), other programs written in potentially different languages could effortlessly interface with the bus once they mimic the serialization format. The last one, however, has already implemented the entire bus functionality in *C++* and *Rust*, besides the Python variant. 

Skip to content 

**Build and run** apps in over 115 regions with MongoDB Atlas, the database for every enterprise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/virtual-interfaces.html 1/2  
7/17/26, 12:50 AM Virtual Interfaces \- python-can 4.6.1 documentation **Common Limitations** 

**Guaranteed delivery** and **message ordering** is one major point of difference: While in a physical CAN network, a message is either sent or in queue (or an explicit error occurred), this may not be the case for virtual networks. The udp\_multicast bus for example, drops this property for the benefit of lower latencies by using unreliable UDP/IP instead of reliable TCP/IP (and because normal IP multicast is inherently unreliable, as the recipients are unknown by design). The other three buses faithfully model a physical CAN network in this regard: They ensure that all recipients actually receive (and acknowledge each message), much like in a physical CAN network. They also ensure that messages are relayed in the order they have arrived at the central server and that messages arrive at the recipients exactly once. Both is not guaranteed to hold for the best-effort udp\_multicast bus as it uses UDP/IP as a transport layer. 

**Central servers** are, however, required by interfaces 3 and 4 (the external tools) to provide these guarantees of message delivery and message ordering. The central servers receive and distribute the CAN messages to all other bus participants, unlike in a real physical CAN network. The first intra process virtual interface only runs within one Python process, effectively the Python instance of VirtualBus acts as a central server. Notably the udp\_multicast bus does not require a central server. 

**Arbitration and throughput** are two interrelated functions/properties of CAN networks which are typically abstracted in virtual interfaces. In all four interfaces, an unlimited amount of messages can be sent per unit of time (given the computational power of the machines and networks that are involved). In a real CAN/CAN FD networks, however, throughput is usually much more restricted and prioritization of arbitration IDs is thus an important feature once the bus is starting to get saturated. None of the interfaces presented above support any sort of throttling or ID arbitration under high loads. 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

stable 

**Build and run** apps in over 115 regions with MongoDB Atlas, the database for every enterprise. 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/virtual-interfaces.html 2/2