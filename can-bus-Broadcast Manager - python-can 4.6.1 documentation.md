7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation **Broadcast Manager**   
The broadcast manager allows the user to setup periodic message jobs. For example sending a particular message at a given period. The broadcast manager supported natively by several interfaces and a software thread based scheduler is used as a fallback. 

This example shows the socketcan backend using the broadcast manager: 

Skip to content 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 1/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation 

 1 *\#\!/usr/bin/env python* 

 2 

 3 *"""* 

 4 *This example exercises the periodic sending capabilities.* 

 5 

 6 *Expects a vcan0 interface:* 

 7 

 8 *python3 \-m examples.cyclic* 

 9 

 10 *"""* 

 11 

 12 **import logging** 

 13 **import time** 

 14 

 15 **import can** 

 16 

 17 logging.basicConfig(level\=logging.INFO) 

 18 

 19 

 20 **def** simple\_periodic\_send(bus): 

 21 *"""* 

 22 *Sends a message every 20ms with no explicit timeout* 

 23 *Sleeps for 2 seconds then stops the task.* 

 24 *"""* 

 25 print("Starting to send a message every 200ms for 2s") 

 26 msg \= can.Message( 

 27 arbitration\_id\=0x123, data\=\[1, 2, 3, 4, 5, 6\], is\_extended\_id\=**False ** 28 ) 

 29 task \= bus.send\_periodic(msg, 0.20) 

 30 **assert** isinstance(task, can.CyclicSendTaskABC) 

 31 time.sleep(2) 

 32 task.stop() 

 33 print("stopped cyclic send") 

 34 

 35 

 36 **def** limited\_periodic\_send(bus): 

 37 *"""Send using LimitedDurationCyclicSendTaskABC."""* 

 38 print("Starting to send a message every 200ms for 1s") 

 39 msg \= can.Message( 

 40 arbitration\_id\=0x12345678, data\=\[0, 0, 0, 0, 0, 0\], is\_extended\_id\=**True**  41 ) 

 42 task \= bus.send\_periodic(msg, 0.20, 1, store\_task\=**False**) 

 43 **if not** isinstance(task, can.LimitedDurationCyclicSendTaskABC): 

 44 print("This interface doesn't seem to support LimitedDurationCyclicSendTaskABC")  45 task.stop() 

 46 **return**   
Skip to content   
 ~~47~~ 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see   
 48 time.sleep(2) 

patterns, not noise.   
 49 print("Cyclic send should have stopped as duration expired") 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 2/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation  50 *\# Note the (finished) task will still be tracked by the Bus*   
 51 *\# unless we pass \`store\_task=False\` to bus.send\_periodic* 

 52 *\# alternatively calling stop removes the task from the bus* 

 53 *\# task.stop()* 

 54 

 55 

 56 **def** test\_periodic\_send\_with\_modifying\_data(bus): 

 57 *"""Send using ModifiableCyclicTaskABC."""* 

 58 print("Starting to send a message every 200ms. Initial data is four consecutive 1s")  59 msg \= can.Message(arbitration\_id\=0x0CF02200, data\=\[1, 1, 1, 1\]) 

 60 task \= bus.send\_periodic(msg, 0.20) 

 61 **if not** isinstance(task, can.ModifiableCyclicTaskABC): 

 62 print("This interface doesn't seem to support modification") 

 63 task.stop() 

 64 **return** 

 65 time.sleep(2) 

 66 print("Changing data of running task to begin with 99") 

 67 msg.data\[0\] \= 0x99 

 68 task.modify\_data(msg) 

 69 time.sleep(2) 

 70 

 71 task.stop() 

 72 print("stopped cyclic send") 

 73 print("Changing data of stopped task to single ff byte") 

 74 msg.data \= bytearray(\[0xFF\]) 

 75 msg.dlc \= 1 

 76 task.modify\_data(msg) 

 77 time.sleep(1) 

 78 print("starting again") 

 79 task.start() 

 80 time.sleep(1) 

 81 task.stop() 

 82 print("done") 

 83 

 84 

 85 *\# Will have to consider how to expose items like this. The socketcan* 

 86 *\# interfaces will continue to support it... but the top level api won't. * 87 *\# def test\_dual\_rate\_periodic\_send():* 

 88 *\# """Send a message 10 times at 1ms intervals, then continue to send every 500ms""" * 89 *\# msg \= can.Message(arbitration\_id=0x123, data=\[0, 1, 2, 3, 4, 5\])*  90 *\# print("Creating cyclic task to send message 10 times at 1ms, then every 500ms") * 91 *\# task \= can.interface.MultiRateCyclicSendTask('vcan0', msg, 10, 0.001, 0.50)*  92 *\# time.sleep(2)* 

 93 *\#* 

 94 *\# print("Changing data\[0\] \= 0x42")* 

 95 *\# msg.data\[0\] \= 0x42* 

 96 *\# task.modify\_data(msg)*   
Skip to content 

 97 *\# time.sleep(2)*   
**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see  98 *\#*   
patterns, not noise.   
 99 *\# task.stop()* 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 3/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation 100 *\# print("stopped cyclic send")*   
101 *\#* 

102 *\# time.sleep(2)* 

103 *\#* 

104 *\# task.start()* 

105 *\# print("starting again")* 

106 *\# time.sleep(2)* 

107 *\# task.stop()* 

108 *\# print("done")* 

109 

110 

111 **def** main(): 

112 *"""Test different cyclic sending tasks."""* 

113 reset\_msg \= can.Message( 

114 arbitration\_id\=0x00, data\=\[0, 0, 0, 0, 0, 0\], is\_extended\_id\=**False** 115 ) 

116 

117 *\# this uses the default configuration (for example from environment variables, or a* 118 *\# config file) see https://python-can.readthedocs.io/en/stable/configuration.html* 119 **with** can.Bus() **as** bus: 

120 bus.send(reset\_msg) 

121 

122 simple\_periodic\_send(bus) 

123 

124 bus.send(reset\_msg) 

125 

126 limited\_periodic\_send(bus) 

127 

128 test\_periodic\_send\_with\_modifying\_data(bus) 

129 

130 *\# print("Carrying out multirate cyclic test for {} interface".format(interface))* 131 *\# can.rc\['interface'\] \= interface* 

132 *\# test\_dual\_rate\_periodic\_send()* 

133 

134 time.sleep(2) 

135 

136 

137 **if** \_\_name\_\_ \== "\_\_main\_\_": 

138 main() 

Skip to content 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 4/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation **Message Sending Tasks** 

The class based api for the broadcast manager uses a series of mixin classes. All mixins inherit from CyclicSendTaskABC which inherits from CyclicTask . 

**class** can.broadcastmanager.**CyclicTask** 

Abstract Base for all cyclic tasks. 

**abstractmethod stop()** 

Cancel this periodic task. 

**RAISES:** 

**CanError** – If stop is called on an already stopped task. 

**RETURN TYPE:** 

None 

**class** can.broadcastmanager.**CyclicSendTaskABC(messages, period)** Message send task with defined period 

**PARAMETERS:** 

**messages** (*Sequence\[Message\] | Message*) – The messages to be sent periodically. **period** (*float*) – The rate in seconds at which to send the messages. 

**RAISES:** 

**ValueError** – If the given messages are invalid   
\[source\] \[source\] 

\[source\] 

**class** can.broadcastmanager.**LimitedDurationCyclicSendTaskABC(messages, period, duration)** 

Message send task with a defined duration and period. 

**PARAMETERS:** 

**messages** (*Sequence\[Message\] | Message*) – The messages to be sent periodically. **period** (*float*) – The rate in seconds at which to send the messages.   
\[source\] 

**duration** (*float | None*) – Approximate duration in seconds to continue sending messages. If no duration is provided, the task will continue indefinitely. 

**RAISES:** 

**ValueError** – If the given messages are invalid 

**class** can.broadcastmanager.**MultiRateCyclicSendTaskABC(channel, messages, count,** 

**initial\_period, subsequent\_period)**   
Skip to content   
~~A Cyclic sen~~d task that supports switches send frequency after a set time. **Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise.   
\[source\] 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 5/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation Transmits a message *count* times at *initial\_period* then continues to transmit messages at *subsequent\_period*. 

**PARAMETERS:** 

**channel** (*int | str | Sequence\[int\]*) – See interface specific documentation. 

**messages** (*Sequence\[Message\] | Message*) 

**count** (*int*) 

**initial\_period** (*float*) 

**subsequent\_period** (*float*) 

**RAISES:** 

**ValueError** – If the given messages are invalid 

**class** can.**ModifiableCyclicTaskABC(messages, period)** 

**PARAMETERS:** 

**messages** (*Sequence\[Message\] | Message*) – The messages to be sent periodically. **period** (*float*) – The rate in seconds at which to send the messages. 

**RAISES:** 

**ValueError** – If the given messages are invalid 

**modify\_data(messages)**   
\[source\] \[source\]   
Update the contents of the periodically sent messages, without altering the timing. 

**PARAMETERS:** 

**messages** (*Sequence\[Message\] | Message*) – 

The messages with the new Message.data . 

Note: The arbitration ID cannot be changed. 

Note: The number of new cyclic messages to be sent must be equal to the original number of messages originally specified for this task. 

**RAISES:** 

**ValueError** – If the given messages are invalid 

**RETURN TYPE:** 

None 

**class** can.**RestartableCyclicTaskABC(messages, period)** 

Skip to content 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise.   
\[source\] 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 6/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation Adds support for restarting a stopped cyclic task 

**PARAMETERS:** 

**messages** (*Sequence\[Message\] | Message*) – The messages to be sent periodically. **period** (*float*) – The rate in seconds at which to send the messages. 

**RAISES:** 

**ValueError** – If the given messages are invalid 

**abstractmethod start()** 

Restart a stopped periodic task. 

**RETURN TYPE:** 

None 

**class** can.broadcastmanager.**ThreadBasedCyclicSendTask(bus, lock, messages, period, duration=None, on\_error=None, autostart=True, modifier\_callback=None)** 

\[source\] \[source\] 

Skip to content 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 7/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation Fallback cyclic send task using daemon thread. 

Transmits *messages* with a *period* seconds for *duration* seconds on a *bus*. 

The *on\_error* is called if any error happens on *bus* while sending *messages*. If *on\_error* present, and returns False when invoked, thread is stopped immediately, otherwise, thread continuously tries to send *messages* ignoring errors on a *bus*. Absence of *on\_error* means that thread exits immediately on error. 

**PARAMETERS:** 

**on\_error** (*Callable\[\[Exception\], bool\] | None*) – The callable that accepts an exception if any error happened on a *bus* while sending *messages*, it shall return either True or False depending on desired behaviour of *ThreadBasedCyclicSendTask*. 

**bus** (*BusABC*) 

**lock** (*lock*) 

**messages** (*Sequence\[Message\] | Message*) 

**period** (*float*) 

**duration** (*float | None*) 

**autostart** (*bool*) 

**modifier\_callback** (*Callable\[\[Message\], None\] | None*) 

**RAISES:** 

**ValueError** – If the given messages are invalid 

**start()** 

Restart a stopped periodic task. 

**RETURN TYPE:** 

None 

**stop()** 

Cancel this periodic task. 

**RAISES:** 

**CanError** – If stop is called on an already stopped task. 

**RETURN TYPE:** 

None 

~~Skip to content~~ 

Copyright ©   
**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see Made with Sphinx and @pradyunsg's Furo   
patterns, not noise.   
\[source\] 

\[source\] 

~~stable~~ 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 8/9  
7/17/26, 12:46 AM Broadcast Manager \- python-can 4.6.1 documentation 

**Stop the vibe-debugging.** Every exception, every backtrace, grouped so you see patterns, not noise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bcm.html 9/9