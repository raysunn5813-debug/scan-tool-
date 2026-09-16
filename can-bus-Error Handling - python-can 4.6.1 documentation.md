7/17/26, 12:47 AM Error Handling \- python-can 4.6.1 documentation **Error Handling**   
There are several specific Exception classes to allow user code to react to specific scenarios related to CAN buses: 

Exception (Python standard library) 

\+-- ... 

\+-- CanError (python\-can) 

 \+-- CanInterfaceNotImplementedError 

 \+-- CanInitializationError 

 \+-- CanOperationError 

 \+-- CanTimeoutError 

Keep in mind that some functions and methods may raise different exceptions. For example, validating typical arguments and parameters might result in a ValueError . This should always be documented for the function at hand. 

**exception** can.exceptions.**CanError(message='', error\_code=None)** Bases: Exception 

Base class for all CAN related exceptions. 

If specified, the error code is automatically appended to the message: 

**\>\>\>** *\# With an error code (it also works with a specific error):* 

**\>\>\>** error \= CanOperationError(message\="Failed to do the thing", error\_code\=42) **\>\>\>** str(error) 

'Failed to do the thing \[Error Code 42\]' 

**\>\>\>** 

**\>\>\>** *\# Missing the error code:* 

**\>\>\>** plain\_error \= CanError(message\="Something went wrong ...") 

**\>\>\>** str(plain\_error) 

'Something went wrong ...' 

**PARAMETERS:**   
\[source\] 

**error\_code** (*int | None*) – An optional error code to narrow down the cause of the fault **error\_code** – An optional error code to narrow down the cause of the fault **message** (*str*) 

**RETURN TYPE:**   
Skip to content 

None   
Build smarter search with MongoDB Atlas — your vector database for AI apps. **Start free.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/errors.html 1/4  
7/17/26, 12:47 AM Error Handling \- python-can 4.6.1 documentation **exception** can.exceptions.**CanInitializationError(message='', error\_code=None)** Bases: CanError 

Indicates an error the occurred while initializing a can.BusABC . 

If initialization fails due to a driver or platform missing/being unsupported, a 

\[source\] 

CanInterfaceNotImplementedError is raised instead. If initialization fails due to a value being out of range, a ValueError is raised. 

**Example scenarios:** 

Try to open a non-existent device and/or channel 

Try to use an invalid setting, which is ok by value, but not ok for the interface The device or other resources are already used 

**PARAMETERS:** 

**message** (*str*) 

**error\_code** (*int | None*) 

**RETURN TYPE:** 

None 

**exception** can.exceptions.**CanInterfaceNotImplementedError(message='', error\_code=None)** 

Bases: CanError , NotImplementedError 

Indicates that the interface is not supported on the current platform. 

**Example scenarios:** 

No interface with that name exists 

The interface is unsupported on the current operating system or interpreter The driver could not be found or has the wrong version 

**PARAMETERS:** 

**message** (*str*) 

**error\_code** (*int | None*) 

**RETURN TYPE:** 

None 

**exception** can.exceptions.**CanOperationError(message='', error\_code=None)** Bases: CanError 

Skip to content   
\[source\] 

\[source\] 

stable 

Build smarter search with MongoDB Atlas — your vector database for AI apps. **Start free.** 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/errors.html 2/4  
7/17/26, 12:47 AM Error Handling \- python-can 4.6.1 documentation Indicates an error while in operation. 

**Example scenarios:** 

A call to a library function results in an unexpected return value An invalid message was received 

The driver rejected a message that was meant to be sent 

Cyclic redundancy check (CRC) failed 

A message remained unacknowledged 

A buffer is full 

**PARAMETERS:** 

**message** (*str*) 

**error\_code** (*int | None*) 

**RETURN TYPE:** 

None 

**exception** can.exceptions.**CanTimeoutError(message='', error\_code=None)** Bases: CanError , TimeoutError 

Indicates the timeout of an operation. 

**Example scenarios:** 

Some message could not be sent after the timeout elapsed 

No message was read within the given time 

**PARAMETERS:** 

**message** (*str*) 

**error\_code** (*int | None*) 

**RETURN TYPE:** 

None 

can.exceptions.**error\_check(error\_message=None, exception\_type=\<class 'can.exceptions.CanOperationError'\>)**   
\[source\] \[source\]   
Catches any exceptions and turns them into the new type while preserving the stack trace. 

**PARAMETERS:** 

**error\_message** (*str | None*) 

**exception\_type** (*type\[CanError\]*)   
Skip to content 

**RETURN TYPE:**   
Build smarter search with MongoDB Atlas — your vector database for AI apps. **Start** 

stable 

*Ads by* 

**free.**   
*Generator*\[None, None, None\]   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/errors.html 3/4  
7/17/26, 12:47 AM Error Handling \- python-can 4.6.1 documentation 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

Build smarter search with MongoDB Atlas — your vector database for AI apps. **Start free.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/errors.html 4/4