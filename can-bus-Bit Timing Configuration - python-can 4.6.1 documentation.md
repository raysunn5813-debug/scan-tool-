7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation **Bit Timing Configuration**   
The CAN protocol, specified in ISO 11898, allows the bitrate, sample point and number of samples to be optimized for a given application. These parameters, known as bit timings, can be adjusted to meet the requirements of the communication system and the physical communication channel. 

These parameters include: 

**tseg1**: The time segment 1 (TSEG1) is the amount of time from the end of the sync segment until the sample point. It is expressed in time quanta (TQ). 

**tseg2**: The time segment 2 (TSEG2) is the amount of time from the sample point until the end of the bit. It is expressed in TQ. 

**sjw**: The synchronization jump width (SJW) is the maximum number of TQ that the controller can resynchronize every bit. 

**sample point**: The sample point is defined as the point in time within a bit where the bus controller samples the bus for dominant or recessive levels. It is typically expressed as a percentage of the bit time. The sample point depends on the bus length and propagation time as well as the information processing time of the nodes. 

Nominal Bit Time 

tseg1 tseg2 

sync\_seg prop\_seg phase\_seg1 phase\_seg2 

1 TQ 

75% Sample Point 

Bit Timing and Sample Point 

For example, consider a bit with a total duration of 8 TQ and a sample point at 75%. The values for TSEG1, TSEG2 and SJW would be 5, 2, and 2, respectively. The sample point would be 6 TQ after the start of the bit, leaving 2 TQ for the information processing by the bus nodes. 

**Note** 

The values for TSEG1, TSEG2 and SJW are chosen such that the sample point is at least 50% of the total bit time. This ensures that there is sufficient time for the signal to stabilize before it is sampled.   
Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 1/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation **Note** 

In CAN FD, the arbitration (nominal) phase and the data phase can have different bit rates. As a result, there are two separate sample points to consider. 

Another important parameter is **f\_clock**: The CAN system clock frequency in Hz. This frequency is used to derive the TQ size from the bit rate. The relationship is f\_clock \= (tseg1+tseg2+1) \* bitrate \* brp . The bit rate prescaler value **brp** is usually determined by the controller and is chosen to ensure that the resulting bit time is an integer value. Typical CAN clock frequencies are 8-80 MHz. 

In most cases, the recommended settings for a predefined set of common bit rates will work just fine. In some cases, however, it may be necessary to specify custom bit timings. The BitTiming and BitTimingFd classes can be used for this purpose to specify bit timings in a relatively interface agnostic manner. 

BitTiming or BitTimingFd can also help you to produce an overview of possible bit timings for your desired bit rate: 

**\>\>\> import contextlib** 

**\>\>\> import can** 

**...** 

**\>\>\>** timings \= set() 

**\>\>\> for** sample\_point **in** range(50, 100): 

**... with** contextlib.suppress(ValueError): 

**...** timings.add( 

**...** can.BitTiming.from\_sample\_point( 

**...** f\_clock\=8\_000\_000, 

**...** bitrate\=250\_000, 

**...** sample\_point\=sample\_point, 

**...** ) 

**...** ) 

**...** 

**\>\>\> for** timing **in** sorted(timings, key\=**lambda** x: x.sample\_point): 

**...** print(timing) 

BR: 250\_000 bit/s, SP: 50.00%, BRP: 2, TSEG1: 7, TSEG2: 8, SJW: 4, BTR: C176h, CLK: 8MHz BR: 250\_000 bit/s, SP: 56.25%, BRP: 2, TSEG1: 8, TSEG2: 7, SJW: 4, BTR: C167h, CLK: 8MHz BR: 250\_000 bit/s, SP: 62.50%, BRP: 2, TSEG1: 9, TSEG2: 6, SJW: 4, BTR: C158h, CLK: 8MHz BR: 250\_000 bit/s, SP: 68.75%, BRP: 2, TSEG1: 10, TSEG2: 5, SJW: 4, BTR: C149h, CLK: 8MHz 

BR: 250\_000 bit/s, SP: 75.00%, BRP: 2, TSEG1: 11, TSEG2: 4, SJW: 4, BTR: C13Ah, CLK: 8MHz BR: 250\_000 bit/s, SP: 81.25%, BRP: 2, TSEG1: 12, TSEG2: 3, SJW: 3, BTR: 812Bh, CLK: 8MHz BR: 250\_000 bit/s, SP: 87.50%, BRP: 2, TSEG1: 13, TSEG2: 2, SJW: 2, BTR: 411Ch, CLK: 8MHz BR: 250\_000 bit/s, SP: 93.75%, BRP: 2, TSEG1: 14, TSEG2: 1, SJW: 1, BTR: 010Dh, CLK: 8MHz 

It is possible to specify CAN 2.0 bit timings using the config file:   
Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 2/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation 

\[default\] 

f\_clock=8000000 

brp=1 

tseg1=5 

tseg2=2 

sjw=1 

nof\_samples=1 

The same is possible for CAN FD: 

\[default\] 

f\_clock=80000000 

nom\_brp=1 

nom\_tseg1=119 

nom\_tseg2=40 

nom\_sjw=40 

data\_brp=1 

data\_tseg1=29 

data\_tseg2=10 

data\_sjw=10 

A dict of the relevant config parameters can be easily obtained by calling dict(timing) or {\*\*timing} where timing is the BitTiming or BitTimingFd instance. 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 3/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Check Configuration for more information about saving and loading configurations. 

**class** can.**BitTiming(f\_clock, brp, tseg1, tseg2, sjw, nof\_samples=1, strict=False)** Bases: Mapping \[ str , int \] 

Representation of a bit timing configuration for a CAN 2.0 bus. 

\[source\] 

The class can be constructed in multiple ways, depending on the information available. The preferred way is using CAN clock frequency, prescaler, tseg1, tseg2 and sjw: 

can.BitTiming(f\_clock\=8\_000\_000, brp\=1, tseg1\=5, tseg2\=1, sjw\=1) 

Alternatively you can set the bitrate instead of the bit rate prescaler: 

can.BitTiming.from\_bitrate\_and\_segments( 

 f\_clock\=8\_000\_000, bitrate\=1\_000\_000, tseg1\=5, tseg2\=1, sjw\=1 

) 

It is also possible to specify BTR registers: 

can.BitTiming.from\_registers(f\_clock\=8\_000\_000, btr0\=0x00, btr1\=0x14) or to calculate the timings for a given sample point: 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 4/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation can.BitTiming.from\_sample\_point(f\_clock\=8\_000\_000, bitrate\=1\_000\_000, sample\_point\=75.0) 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**brp** (*int*) – Bit rate prescaler. 

**tseg1** (*int*) – Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point. 

**tseg2** (*int*) – Time segment 2, that is, the number of quanta from the sampling point to the end of the bit. 

**sjw** (*int*) – The Synchronization Jump Width. Decides the maximum number of time quanta that the controller can resynchronize every bit. 

**nof\_samples** (*int*) – Either 1 or 3\. Some CAN controllers can also sample each bit three times. In this case, the bit will be sampled three quanta in a row, with the last sample being taken in the edge between TSEG1 and TSEG2. Three samples should only be used for relatively slow baudrates. 

**strict** (*bool*) – If True, restrict bit timings to the minimum required range as defined in ISO 11898\. This can be used to ensure compatibility across a wide variety of CAN hardware. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**classmethod from\_bitrate\_and\_segments(f\_clock, bitrate, tseg1, tseg2, sjw,** 

**nof\_samples=1, strict=False)** 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.**   
\[source\] 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 5/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Create a BitTiming instance from bitrate and segment lengths. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**bitrate** (*int*) – Bitrate in bit/s. 

**tseg1** (*int*) – Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point. 

**tseg2** (*int*) – Time segment 2, that is, the number of quanta from the sampling point to the end of the bit. 

**sjw** (*int*) – The Synchronization Jump Width. Decides the maximum number of time quanta that the controller can resynchronize every bit. 

**nof\_samples** (*int*) – Either 1 or 3\. Some CAN controllers can also sample each bit three times. In this case, the bit will be sampled three quanta in a row, with the last sample being taken in the edge between TSEG1 and TSEG2. Three samples should only be used for relatively slow baudrates. 

**strict** (*bool*) – If True, restrict bit timings to the minimum required range as defined in ISO 11898\. This can be used to ensure compatibility across a wide variety of CAN hardware. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*BitTiming* 

**classmethod from\_registers(f\_clock, btr0, btr1)** 

Create a BitTiming instance from registers btr0 and btr1. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**btr0** (*int*) – The BTR0 register value used by many CAN controllers. **btr1** (*int*) – The BTR1 register value used by many CAN controllers. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*BitTiming* 

**classmethod iterate\_from\_sample\_point(f\_clock, bitrate, sample\_point=69.0)** Skip to content   
\[source\] 

\[source\] 

stable 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 6/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Create a BitTiming iterator with all the solutions for a sample point. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**bitrate** (*int*) – Bitrate in bit/s. 

**sample\_point** (*int*) – The sample point value in percent. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*Iterator*\[*BitTiming*\] 

**classmethod from\_sample\_point(f\_clock, bitrate, sample\_point=69.0)** Create a BitTiming instance for a sample point. 

\[source\] 

This function tries to find bit timings, which are close to the requested sample point. It does not take physical bus properties into account, so the calculated bus timings might not work properly for you. 

The oscillator\_tolerance() function might be helpful to evaluate the bus timings. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**bitrate** (*int*) – Bitrate in bit/s. 

**sample\_point** (*int*) – The sample point value in percent. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*BitTiming* 

**property f\_clock: int** 

The CAN system clock frequency in Hz. 

**property bitrate: int** 

Bitrate in bits/s. 

**property brp: int** 

Bit Rate Prescaler. 

**property tq: int**   
Skip to content 

Time quantum in nanoseconds   
You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 7/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation **property nbt: int** 

Nominal Bit Time. 

**property tseg1: int** 

Time segment 1\. 

The number of quanta from (but not including) the Sync Segment to the sampling point. 

**property tseg2: int** 

Time segment 2\. 

The number of quanta from the sampling point to the end of the bit. 

**property sjw: int** 

Synchronization Jump Width. 

**property nof\_samples: int** 

Number of samples (1 or 3). 

**property sample\_point: float** 

Sample point in percent. 

**property btr0: int** 

Bit timing register 0 for SJA1000. 

**property btr1: int** 

Bit timing register 1 for SJA1000. 

**oscillator\_tolerance(node\_loop\_delay\_ns=250.0, bus\_length\_m=10.0)** Oscillator tolerance in percent according to ISO 11898-1. 

**PARAMETERS:** 

**node\_loop\_delay\_ns** (*float*) – Transceiver loop delay in nanoseconds. **bus\_length\_m** (*float*) – Bus length in meters. 

**RETURN TYPE:** 

float 

**recreate\_with\_f\_clock(f\_clock)** 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you**   
\[source\] 

\[source\] 

stable 

*Ads by* 

**need is Atlas.**   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 8/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Return a new BitTiming instance with the given *f\_clock* but the same bit rate and sample point. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**RAISES:** 

**ValueError** – if no suitable bit timings were found. 

**RETURN TYPE:** 

*BitTiming* 

**class** can.**BitTimingFd(f\_clock, nom\_brp, nom\_tseg1, nom\_tseg2, nom\_sjw, data\_brp,** 

**data\_tseg1, data\_tseg2, data\_sjw, strict=False)** Bases: Mapping \[ str , int \] 

Representation of a bit timing configuration for a CAN FD bus.   
\[source\] 

The class can be constructed in multiple ways, depending on the information available. The preferred way is using CAN clock frequency, bit rate prescaler, tseg1, tseg2 and sjw for both the arbitration (nominal) and data phase: 

can.BitTimingFd( 

 f\_clock\=80\_000\_000, 

 nom\_brp\=1, 

 nom\_tseg1\=59, 

 nom\_tseg2\=20, 

 nom\_sjw\=10, 

 data\_brp\=1, 

 data\_tseg1\=6, 

 data\_tseg2\=3, 

 data\_sjw\=2, 

) 

Alternatively you can set the bit rates instead of the bit rate prescalers: 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 9/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation 

can.BitTimingFd.from\_bitrate\_and\_segments( 

 f\_clock\=80\_000\_000, 

 nom\_bitrate\=1\_000\_000, 

 nom\_tseg1\=59, 

 nom\_tseg2\=20, 

 nom\_sjw\=10, 

 data\_bitrate\=8\_000\_000, 

 data\_tseg1\=6, 

 data\_tseg2\=3, 

 data\_sjw\=2, 

) 

It is also possible to calculate the timings for a given pair of arbitration and data sample points: 

can.BitTimingFd.from\_sample\_point( 

 f\_clock\=80\_000\_000, 

 nom\_bitrate\=1\_000\_000, 

 nom\_sample\_point\=75.0, 

 data\_bitrate\=8\_000\_000, 

 data\_sample\_point\=70.0, 

) 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 10/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Initialize a BitTimingFd instance with the specified parameters. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**nom\_brp** (*int*) – Nominal (arbitration) phase bitrate prescaler. 

**nom\_tseg1** (*int*) – Nominal phase Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point. 

**nom\_tseg2** (*int*) – Nominal phase Time segment 2, that is, the number of quanta from the sampling point to the end of the bit. 

**nom\_sjw** (*int*) – The Synchronization Jump Width for the nominal phase. This value determines the maximum number of time quanta that the controller can resynchronize every bit. 

**data\_brp** (*int*) – Data phase bitrate prescaler. 

**data\_tseg1** (*int*) – Data phase Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point. 

**data\_tseg2** (*int*) – Data phase Time segment 2, that is, the number of quanta from the sampling point to the end of the bit. 

**data\_sjw** (*int*) – The Synchronization Jump Width for the data phase. This value determines the maximum number of time quanta that the controller can resynchronize every bit. **strict** (*bool*) – If True, restrict bit timings to the minimum required range as defined in ISO 11898\. This can be used to ensure compatibility across a wide variety of CAN hardware. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**classmethod from\_bitrate\_and\_segments(f\_clock, nom\_bitrate, nom\_tseg1, nom\_tseg2,** 

**nom\_sjw, data\_bitrate, data\_tseg1, data\_tseg2, data\_sjw, strict=False)** Skip to content   
\[source\] 

stable 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 11/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Create a BitTimingFd instance with the bitrates and segments lengths. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**nom\_bitrate** (*int*) – Nominal (arbitration) phase bitrate in bit/s. 

**nom\_tseg1** (*int*) – Nominal phase Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point. 

**nom\_tseg2** (*int*) – Nominal phase Time segment 2, that is, the number of quanta from the sampling point to the end of the bit. 

**nom\_sjw** (*int*) – The Synchronization Jump Width for the nominal phase. This value determines the maximum number of time quanta that the controller can resynchronize every bit. 

**data\_bitrate** (*int*) – Data phase bitrate in bit/s. 

**data\_tseg1** (*int*) – Data phase Time segment 1, that is, the number of quanta from (but not including) the Sync Segment to the sampling point. 

**data\_tseg2** (*int*) – Data phase Time segment 2, that is, the number of quanta from the sampling point to the end of the bit. 

**data\_sjw** (*int*) – The Synchronization Jump Width for the data phase. This value determines the maximum number of time quanta that the controller can resynchronize every bit. 

**strict** (*bool*) – If True, restrict bit timings to the minimum required range as defined in ISO 11898\. This can be used to ensure compatibility across a wide variety of CAN hardware. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*BitTimingFd* 

**classmethod iterate\_from\_sample\_point(f\_clock, nom\_bitrate, nom\_sample\_point,** 

**data\_bitrate, data\_sample\_point)** 

Skip to content 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.**   
\[source\] 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 12/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation Create an BitTimingFd iterator with all the solutions for a sample point. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**nom\_bitrate** (*int*) – Nominal bitrate in bit/s. 

**nom\_sample\_point** (*int*) – The sample point value of the arbitration phase in percent. **data\_bitrate** (*int*) – Data bitrate in bit/s. 

**data\_sample\_point** (*int*) – The sample point value of the data phase in percent. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*Iterator*\[*BitTimingFd*\] 

**classmethod from\_sample\_point(f\_clock, nom\_bitrate, nom\_sample\_point, data\_bitrate,** 

**data\_sample\_point)** 

Create a BitTimingFd instance for a sample point.   
\[source\] 

This function tries to find bit timings, which are close to the requested sample points. It does not take physical bus properties into account, so the calculated bus timings might not work properly for you. 

The oscillator\_tolerance() function might be helpful to evaluate the bus timings. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**nom\_bitrate** (*int*) – Nominal bitrate in bit/s. 

**nom\_sample\_point** (*int*) – The sample point value of the arbitration phase in percent. **data\_bitrate** (*int*) – Data bitrate in bit/s. 

**data\_sample\_point** (*int*) – The sample point value of the data phase in percent. 

**RAISES:** 

**ValueError** – if the arguments are invalid. 

**RETURN TYPE:** 

*BitTimingFd* 

**property f\_clock: int** 

The CAN system clock frequency in Hz. 

**property nom\_bitrate: int**   
Skip to content 

Nominal (arbitration phase) bitrate.   
You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 13/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation **property nom\_brp: int** 

Prescaler value for the arbitration phase. 

**property nom\_tq: int** 

Nominal time quantum in nanoseconds 

**property nbt: int** 

Number of time quanta in a bit of the arbitration phase. 

**property nom\_tseg1: int** 

Time segment 1 value of the arbitration phase. 

This is the sum of the propagation time segment and the phase buffer segment 1\. 

**property nom\_tseg2: int** 

Time segment 2 value of the arbitration phase. Also known as phase buffer segment 2\. 

**property nom\_sjw: int** 

Synchronization jump width of the arbitration phase. 

The phase buffer segments may be shortened or lengthened by this value. 

**property nom\_sample\_point: float** 

Sample point of the arbitration phase in percent. 

**property data\_bitrate: int** 

Bitrate of the data phase in bit/s. 

**property data\_brp: int** 

Prescaler value for the data phase. 

**property data\_tq: int** 

Data time quantum in nanoseconds 

**property dbt: int** 

Number of time quanta in a bit of the data phase. 

**property data\_tseg1: int** 

TSEG1 value of the data phase. 

This is the sum of the propagation time segment and the phase buffer segment 1\. 

Skip to content   
**property data\_tseg2: int**   
You don't need a separate datab~~ase~~ to start building gen AI-powered apps. **All you** TSEG2 value of the data phase. Also known as phase buffer segment 2\.   
**need is Atlas.** 

stable 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 14/15  
7/17/26, 12:47 AM Bit Timing Configuration \- python-can 4.6.1 documentation **property data\_sjw: int** 

Synchronization jump width of the data phase. 

The phase buffer segments may be shortened or lengthened by this value. 

**property data\_sample\_point: float** 

Sample point of the data phase in percent. 

**oscillator\_tolerance(node\_loop\_delay\_ns=250.0, bus\_length\_m=10.0)** Oscillator tolerance in percent according to ISO 11898-1. 

**PARAMETERS:** 

**node\_loop\_delay\_ns** (*float*) – Transceiver loop delay in nanoseconds. **bus\_length\_m** (*float*) – Bus length in meters. 

**RETURN TYPE:** 

float 

**recreate\_with\_f\_clock(f\_clock)** 

\[source\] \[source\]   
Return a new BitTimingFd instance with the given *f\_clock* but the same bit rates and sample points. 

**PARAMETERS:** 

**f\_clock** (*int*) – The CAN system clock frequency in Hz. 

**RAISES:** 

**ValueError** – if no suitable bit timings were found. 

**RETURN TYPE:** 

*BitTimingFd* 

Copyright © 

Made with Sphinx and @pradyunsg's Furo 

stable 

You don't need a separate database to start building gen AI-powered apps. **All you need is Atlas.** 

*Ads by*   
*EthicalAds***Close Ad** 

https://python-can.readthedocs.io/en/stable/bit\_timing.html 15/15