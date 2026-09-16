7/17/26, 12:48 AM Utilities \- python-can 4.6.1 documentation **Utilities**   
can.**detect\_available\_configs(interfaces=None, timeout=5.0)** 

Detect all configurations/channels that the interfaces could currently connect with. This might be quite time-consuming. 

\[source\] 

Automated configuration detection may not be implemented by every interface on every platform. This method will not raise an error in that case, but will rather return an empty list for that interface. 

**PARAMETERS:** 

**interfaces** (*None | str | Iterable\[str\]*) – either \- the name of an interface to be searched in as a string, \- an iterable of interface names to search in, or \- *None* to search in all known interfaces. 

**timeout** (*float*) – maximum number of seconds to wait for all interface detection tasks to complete. If exceeded, any pending tasks will be cancelled, a warning will be logged, and the method will return results gathered so far. 

**RETURN TYPE:** 

list\[dict\] 

**RETURNS:** 

an iterable of dicts, each suitable for usage in the constructor of can.BusABC . Interfaces that timed out will be logged as warnings and excluded. 

can.cli.**add\_bus\_arguments(parser, \*, filter\_arg=False, prefix=None, group\_title=None)** 

Adds CAN bus configuration options to an argument parser. **PARAMETERS:**   
\[source\] 

**parser** (*ArgumentParser*) – The argument parser to which the options will be added. **filter\_arg** (*bool*) – Whether to include the filter argument. 

**prefix** (*str | None*) – An optional prefix for the argument names, allowing configuration of multiple buses. 

**group\_title** (*str | None*) – The title of the argument group. If not provided, a default title will be generated based on the prefix. For example, “bus arguments (prefix)” if a prefix is specified, or “bus arguments” otherwise. 

**RETURN TYPE:**   
Skip to content 

None   
**Build and run** apps in over 115 regions with MongoDB Atlas, the database for every enterprise. 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/utils.html 1/2  
7/17/26, 12:48 AM Utilities \- python-can 4.6.1 documentation 

can.cli.**create\_bus\_from\_namespace(namespace, \*, prefix=None, \*\*kwargs)** \[source\] Creates and returns a CAN bus instance based on the provided namespace and arguments. 

**PARAMETERS:** 

**namespace** (*Namespace*) – The namespace containing parsed arguments. 

**prefix** (*str | None*) – An optional prefix for the argument names, enabling support for multiple buses. 

**kwargs** (*Any*) – Additional keyword arguments to configure the bus. 

**RETURNS:** 

A CAN bus instance. 

**RETURN TYPE:** 

*BusABC* 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

stable 

**Build and run** apps in over 115 regions with MongoDB Atlas, the database for every enterprise. 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/utils.html 2/2