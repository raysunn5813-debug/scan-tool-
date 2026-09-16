7/17/26, 12:51 AM Plugin Interface \- python-can 4.6.1 documentation **Plugin Interface**   
External packages can register new interfaces by using the can.interface entry point in its project configuration. The format of the entry point depends on your project configuration format (*pyproject.toml*, *setup.cfg* or *setup.py*). 

In the following example module defines the location of your bus class inside your package e.g. my\_package.subpackage.bus\_module and classname is the name of your can.BusABC subclass. 

**pyproject.toml (PEP 621\) setup.cfg setup.py** 

*\# Note the quotes around can.interface in order to escape the dot .* 

**\[project.entry-points.**"can.interface"**\]** 

interface\_name \= "module:classname" 

The interface\_name can be used to create an instance of the bus in the **python-can** API: 

**import can** 

bus \= can.Bus(interface\="interface\_name", channel\=0) 

**Example Interface Plugins** 

The table below lists interface drivers that can be added by installing additional packages that utilise the plugin API. These modules are optional dependencies of python-can. 

**Note** 

The packages listed below are maintained by other authors. Any issues should be reported in their corresponding repository and **not** in the python-can repository. 

Skip to content 

**This isn't a stack. It's a pile.** Errors, perf, logs, hosts. One tool, one bill, built 4 devs who ship 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/plugin-interface.html 1/2  
7/17/26, 12:51 AM Plugin Interface \- python-can 4.6.1 documentation **Name Description** 

python-can-canine CAN Driver for the CANine CAN interface 

python-can-cvector Cython based version of the ‘VectorBus’ 

python-can-remote CAN over network bridge 

python-can-sontheim CAN Driver for Sontheim CAN interfaces (e.g. CANfox) zlgcan Python wrapper for zlgcan-driver-rs 

python-can-cando Python wrapper for Netronics’ CANdo and CANdoISO python-can-candle A full-featured driver for candleLight 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

stable 

**This isn't a stack. It's a pile.** Errors, perf, logs, hosts. One tool, one bill, built 4 devs who ship 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/plugin-interface.html 2/2