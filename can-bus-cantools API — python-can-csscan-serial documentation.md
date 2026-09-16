Docs » **python-can** API » **cantools** API 

**cantools** API 

 **Warning** 

The examples on this page are **provided without support** 

The Python package **cantools** extends **python-can** with support for databases (containing message interpretations) and support for message payload encoding/decoding. Refer to the **cantools** documentation for more information https://cantools.readthedocs.io/. 

This page contains some basic examples on how to use **cantools**. 

Installation 

**$** pip install cantools

 **Note** 

The examples on this page has been tested with version 39.4.13 of cantools 

Manually define database 

A database of message interpretations can be *manually* constructed directly in Python.   
**from cantools.database import** Database, Message, Signal 

**from cantools.database.conversion import** BaseConversion 

*\# Define signals* 

db\_msg1\_signals \= \[ 

 Signal(name\="A1", start\=0, length\=16, conversion\=BaseConversion.factory(scale\=0.625, offset\=0)), 

 Signal(name\="A2", start\=16, length\=16, conversion\=BaseConversion.factory(scale\=0.625, offset\=0)), 

 Signal(name\="A3", start\=32, length\=16, conversion\=BaseConversion.factory(scale\=0.625, offset\=0)), 

 Signal(name\="A4", start\=48, length\=16, conversion\=BaseConversion.factory(scale\=0.625, offset\=0))   
\] 

*\# Define messages* 

db\_msgs \= \[ 

 Message(name\="A1ToA4", is\_extended\_frame\=**False**, frame\_id\=2, length\=8, signals\=db\_msg1\_signals) \] 

*\# Define database* 

db \= Database(messages\=db\_msgs) 

Load existing database 

**cantools** supports a range of database file formats. e.g. \*.DBC . 

**from cantools import** database 

*\# Load database from file* 

db \= database.load\_file("\<DBC\_FILE\_PATH\>")

Decode messages 

Below example demonstrates how **cantools** can be used to decode messages. 

 **Note** 

Alternatively, messages can be logged to a file (see can-logger) and decoded later.   
**import can** 

**from cantools import** database 

*\# Load database from file* 

db \= database.load\_file("\<DBC\_FILE\_PATH\>") 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Receive messages* 

 **for** msg **in** bus: 

 *\# Get message name from database* 

 **try**: 

 db\_msg \= db.get\_message\_by\_frame\_id(msg.arbitration\_id) 

 **except KeyError**: 

 *\# Message not defined in database* 

 **continue** 

 *\# Decode using database* 

 result \= db.decode\_message(db\_msg.name, data\=msg.data) 

 *\# Add timestamp* 

 result.update({"t": msg.timestamp}) 

 print(f"**{**db\_msg.name**}**: **{**result**}**")

**cantools** has weak support for J1939 PGNs. However, by splitting the database into two (one for PDU format 1 and one for PDU format 2), decoding of PGNs can be done as demonstrated below. 

 **Note** 

For better J1939 support, consider using the dedicated **python-can-j1939** package.   
**import can** 

**import math** 

**from cantools import** database, j1939 

**from collections import** defaultdict 

*\# Create a J1939 PDU1 and PDU2 database (with matching PGN ID masks)* db\_pdu1 \= database.Database(frame\_id\_mask\=0x3FF0000) 

db\_pdu2 \= database.Database(frame\_id\_mask\=0x3FFFF00) 

*\# Load database from file* 

**for** db\_msg **in** database.load\_file("\<DBC\_FILE\_PATH\>").messages: 

 **if** j1939.is\_pdu\_format\_1(j1939.frame\_id\_unpack(db\_msg.frame\_id).pdu\_format):  db\_pdu1.messages.append(db\_msg)   
 **else**: 

 db\_pdu2.messages.append(db\_msg) 

db\_pdu1.refresh() 

db\_pdu2.refresh() 

*\# Decoded signals storage* 

results \= defaultdict(list) 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Receive messages* 

 **for** msg **in** bus: 

 *\# J1939 is extended only* 

 **if not** msg.is\_extended\_id: 

 **continue** 

 *\# Select database based on PDU format* 

 **if** j1939.is\_pdu\_format\_1(j1939.frame\_id\_unpack(msg.arbitration\_id).pdu\_format):  db \= db\_pdu1 

 **else**: 

 db \= db\_pdu2 

 *\# Get message name from database* 

 **try**: 

 db\_msg \= db.get\_message\_by\_frame\_id(msg.arbitration\_id)  **except KeyError**: 

 *\# Message not defined in database* 

 **continue** 

 *\# Decode using database* 

 result \= db.decode\_message(db\_msg.name, data\=msg.data) 

 *\# Ensure that signals satisfy min/max* 

 **for** name, value **in** result.items(): 

 db\_sig \= db\_msg.get\_signal\_by\_name(name) 

 **if not** db\_sig.maximum \> value \> db\_sig.minimum: 

 result\[name\] \= math.nan 

 *\# Add timestamp* 

 result.update({"t": msg.timestamp}) 

 *\# Append to results* 

 results\[db\_msg.name\].append(result) 

 print(result)  
Encode messages 

Below example demonstrates how **cantools** can be used to encode messages. The example assumes that the database contains a message *Analog1To4* with signals *Analog1*, *Analog2*, *Analog3*, and *Analog4*. 

**import can** 

**from cantools import** database 

*\# Load database* 

db \= database.load\_file("\<DBC\_FILE\_PATH\>") 

*\# Open bus* 

**with** can.Bus(interface\="csscan\_serial", channel\="\<CHANNEL\>") **as** bus: 

 *\# Get message to transmit* 

 db\_msg \= db.get\_message\_by\_name("Analog1To4") 

 *\# Encode data* 

 data \= db\_msg.encode({"Analog1": 0, "Analog2": 2500, "Analog3": 5000, "Analog4": 7500}) 

 *\# Transmit message with encoded data* 

 bus.send(can.Message(arbitration\_id\=db\_msg.frame\_id, 

 is\_extended\_id\=db\_msg.is\_extended\_frame, 

 data\=data))