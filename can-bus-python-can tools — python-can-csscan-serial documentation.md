Docs » **python-can** tools 

**python-can** tools 

**python-can** comes with a range of useful command-line tools (similar to Linux *can-utils*). For more information see https://python-can.readthedocs.io/en/v4.5.0/scripts.html. 

This page includes examples on how to use **python-can** tools relevant to the **python-can csscan-serial** package. 

 **Note** 

The examples on this page assume that the **python-can-csscan-serial** package has been installed and the Python environment is active. 

can-logger 

The *can-logger* tool (similar to can-utils *candump*) can be used to display live CAN-bus traffic or log to a file. The tool supports a range of logging file formats. For more information see https://python-can.readthedocs.io/en/v4.5.0/scripts.html\#can-logger. 

*can-logger, to screen* 

**$** can\_logger \--interface csscan\_serial \--channel COM1 

Connected to csscan\_serial: CSSCAN serial on COM1 

Can Logger (Started on 2024-01-01 12:00:00.000000) 

Timestamp: 1707830060.859518 ID: 003 S Rx DL: 8 00 00 00 00 00 00 00 00 Timestamp: 1707830060.859518 ID: 002 S Rx DL: 8 00 00 00 00 10 00 10 00 Timestamp: 1707830060.867518 ID: 003 S Rx DL: 8 00 00 00 00 00 00 00 00 Timestamp: 1707830060.867518 ID: 002 S Rx DL: 8 00 00 00 00 10 00 10 00 Timestamp: 1707830060.880518 ID: 003 S Rx DL: 8 00 00 00 00 00 00 00 00 Timestamp: 1707830060.880518 ID: 002 S Rx DL: 8 00 00 00 00 10 00 10 00 Timestamp: 1707830060.887518 ID: 003 S Rx DL: 8 00 00 00 00 00 00 00 00 ...

*can-logger, to log dump.log*   
**$** can\_logger \--interface csscan\_serial \--channel COM1 \-f F:/dump.log 

Connected to CSSCANSerial: CSSCAN serial on COM1 

Can Logger (Started on 2024-01-01 12:00:00.000000) 

can-viewer 

 **Note** 

On Windows, can-viewer depends on the windows-curses library which can be installed with pip install python-can\[viewer\] 

The *can-viewer* tool (similar to can-utils *cansniffer*) can be used to display a table of received messages. Run can\_viewer \-h for at list of shortcuts. For more information see https://python can.readthedocs.io/en/v4.5.0/scripts.html\#can-viewer 

*can-viewer, to screen* 

**$** can\_viewer \--interface csscan\_serial \--channel COM1 

Count Time dt ID DLC Data 

7 0.600 0.101 0x003 8 00 00 00 00 00 00 00 00 

7 0.600 0.101 0x002 8 00 00 00 00 10 00 10 00 

7 0.600 0.101 0x001 4 99 99 99 99 

The can-viewer tool also supports simple live decoding using the \-d argument. 

*rules.txt* 

2:\<HHHH:0.625:0.625:0.625:0.625 

3:\<HHHH:0.625:0.625:0.625:0.625

*can-viewer, to screen with decoding rules defined in rules.txt*   
**$** can\_viewer \--interface csscan\_serial \--channel COM1 \-d rules.txt 

Count Time dt ID DLC Data Parsed values 590 58.899 0.099 0x003 8 20 3E 80 1A 40 3E A0 1A 25446.4 10854.4 25497.6 10905.6 

590 58.899 0.099 0x002 8 20 3E 80 1A 50 3E B0 1A 25446.4 10854.4 25523.2 10931.2

 **Note** 

See the can-viewer help for information on the signal decoding syntax. 