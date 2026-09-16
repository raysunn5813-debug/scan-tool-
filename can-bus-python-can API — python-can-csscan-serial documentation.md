Docs » **python-can** API 

**python-can** API 

The **python-can** module is imported with: 

**import can** 

The two main **python-can** objects are: 

1   
Bus : Defines a CAN-bus interface 

2   
Message : Defines a CAN-bus message (containing timestamp, ID, data, and more) 

Detect interfaces 

The **python-can** package supports auto-detection of available interfaces. 

*Detect interface on Windows* 

**\>\>\>** can.detect\_available\_configs("csscan\_serial") 

\[{'interface': 'csscan\_serial', 'channel': 'COM19'}\] 

*Detect interface on Linux* 

**\>\>\>** can.detect\_available\_configs("csscan\_serial") 

\[{'interface': 'csscan\_serial', 'channel': '/dev/ttyACM0'}\]

Auto-detection can be used to automatically find and open a bus.   
**import can** 

*\# Detect busses* 

configs \= can.detect\_available\_configs("csscan\_serial") 

**assert** len(configs) \== 1 

*\# Open bus* 

**with** can.Bus(interface\=configs\[0\]\["interface"\], channel\=configs\[0\]\["channel"\]) **as** bus:  ... 

Receive messages 

The most basic way of receiving messages is demonstrated below. 

**import can** 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Receive messages* 

 **for** msg **in** bus: 

 print(msg)

The **python-can** notifier can be used for more advanced use-cases. Below demonstrates how to use the existing **python-can** Printer and Logger together with a custom Listener .   
**import can** 

**from time import** sleep 

**class CustomListener**(can.Listener): 

 **def** on\_message\_received(self, msg: can.Message) \-\> **None**: 

 *\# Some custom handling of received messages* 

 **pass** 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Printer (prints formatted messages to screen)* 

 print\_listener \= can.Printer() 

 *\# Logger (logs formatted messages to file)* 

 log\_listener \= can.Logger("out.log") 

 *\# Custom listener (invokes listener call-back when message received)* 

 custom\_listener \= CustomListener() 

 *\# Create notifier with printer, logger, and custom listeners* 

 notifier \= can.Notifier(bus, listeners\=\[print\_listener, log\_listener, custom\_listener\])  sleep(10)   
 notifier.stop() 

For more information, see https://python-can.readthedocs.io/en/v4.5.0/notifier.html\#notifier. 

Transmit messages 

The most basic way of transmitting messages is demonstrated below. 

**import can** 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Transmit message* 

 bus.send(can.Message(arbitration\_id\=0x123, is\_extended\_id\=**False**, data\=\[0x01, 0x23, 0x45, 0x67\]))

Periodic transmit messages can be configured using the **python-can** broadcast-manager , see https://python-can.readthedocs.io/en/v4.5.0/bcm.html.   
Replay messages 

Logged messages can be replayed to any interface supported by **python-can** (e.g. csscan\_serial) as demonstrated below. 

**import can** 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Open log file* 

 **with** can.LogReader("\<LOG\_FILE\_PATH\>") **as** reader: 

 *\# Read messages using MessageSync to maintain original scheduling*  **for** msg **in** can.MessageSync(reader): 

 *\# Replay message* 

 bus.send(msg)

\[1\] see https://python-can.readthedocs.io/en/v4.5.0/bus.html 

\[2\] see https://python-can.readthedocs.io/en/v4.5.0/message.html 