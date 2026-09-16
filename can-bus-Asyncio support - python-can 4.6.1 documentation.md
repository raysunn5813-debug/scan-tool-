7/17/26, 12:46 AM Asyncio support \- python-can 4.6.1 documentation **Asyncio support**   
The asyncio module built into Python 3.4 and later can be used to write asynchronous code in a single thread. This library supports receiving messages asynchronously in an event loop using the can.Notifier class. 

There will still be one thread per CAN bus but the user application will execute entirely in the event loop, allowing simpler concurrency without worrying about threading issues. Interfaces that have a valid file descriptor will however be supported natively without a thread. 

You can also use the can.AsyncBufferedReader listener if you prefer to write coroutine based code instead of using callbacks. 

**Example** 

Here is an example using both callback and coroutine based code: 

Skip to content 

stable 

Develop and launch modern apps with MongoDB Atlas, a resilient data platform. *Ads by EthicalAds* **Close Ad** https://python-can.readthedocs.io/en/stable/asyncio.html 1/3  
7/17/26, 12:46 AM Asyncio support \- python-can 4.6.1 documentation *\#\!/usr/bin/env python* 

*"""* 

*This example demonstrates how to use async IO with python-can.* 

*"""* 

**import asyncio** 

**from typing import** TYPE\_CHECKING 

**import can** 

**if** TYPE\_CHECKING: 

 **from can.notifier import** MessageRecipient 

**def** print\_message(msg: can.Message) \-\> **None**: 

 *"""Regular callback function. Can also be a coroutine."""* 

 print(msg) 

**async def** main() \-\> **None**: 

 *"""The main function that runs in the loop."""* 

 **with** can.Bus( 

 interface\="virtual", channel\="my\_channel\_0", receive\_own\_messages\=**True**  ) **as** bus: 

 reader \= can.AsyncBufferedReader() 

 logger \= can.Logger("logfile.asc") 

 listeners: list\[MessageRecipient\] \= \[ 

 print\_message, *\# Callback function* 

 reader, *\# AsyncBufferedReader() listener* 

 logger, *\# Regular Listener object* 

 \] 

 *\# Create Notifier with an explicit loop to use for scheduling of callbacks*  **with** can.Notifier(bus, listeners, loop\=asyncio.get\_running\_loop()):  *\# Start sending first message* 

 bus.send(can.Message(arbitration\_id\=0)) 

 print("Bouncing 10 messages...") 

 **for** \_ **in** range(10): 

 *\# Wait for next message from AsyncBufferedReader* 

 msg \= **await** reader.get\_message() 

 *\# Delay response* 

 **await** asyncio.sleep(0.5) 

 msg.arbitration\_id \+= 1   
Skip to content   
 bus.send(msg) 

stable 

Develop and launch modern apps with MongoDB Atlas, a resilient data platform. *Ads by EthicalAds* **Close Ad**  *\# Wait for last message to arrive* 

https://python-can.readthedocs.io/en/stable/asyncio.html 2/3  
7/17/26, 12:46 AM Asyncio support \- python-can 4.6.1 documentation  **await** reader.get\_message()   
 print("Done\!") 

**if** \_\_name\_\_ \== "\_\_main\_\_": 

 asyncio.run(main()) 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

stable 

Develop and launch modern apps with MongoDB Atlas, a resilient data platform. *Ads by EthicalAds* **Close Ad** https://python-can.readthedocs.io/en/stable/asyncio.html 3/3