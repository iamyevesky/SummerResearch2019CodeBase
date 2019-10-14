# -*- coding: utf-8 -*-
"""
:Created on Tue Jun  4 16:35:26 2019
:Author:   Sena Yevenyo.
:Program:  Reads data from Opsens-PicoM Sensor.
:Return:   Recorded temperatures in list [time, temp] format
           as data1.
:Return:   Recorded temperature in list [temp] format in delay*ntimes seconds
           as data0.
"""

"""
:Log Details:

Machine Details:
   Platform ID:    Windows-10-10.0.14393-SP0
   Processor:      Intel64 Family 6 Model 158 Stepping 9, GenuineIntel

Python:
   Implementation: CPython
   Executable:     C:\Anaconda3\python.exe
   Version:        3.6.3
   Compiler:       MSC v.1900 64 bit (AMD64)
   Bits:           64bit
   Build:          Oct 15 2017 03:27:45 (#default)
   Unicode:        UCS4

PyVISA Version: 1.9.0

Backends:
   ni:
      Version: 1.9.0 (bundled with PyVISA)
      #1: C:\windows\system32\visa32.dll:
         found by: auto
         bitness: 64
         Vendor: National Instruments
         Impl. Version: 5243905
         Spec. Version: 5243136
      #2: C:\windows\system32\visa64.dll:
         found by: auto
         bitness: 64
         Vendor: National Instruments
         Impl. Version: 5243905
         Spec. Version: 5243136
"""
ntimes = 100
delay = 0.02
import pyvisa, time
from pyvisa import constants

"""
:IDE:   Anaconda Spyder Python 3.6
readme: Always .open() and .close() opsens ResourceManager object
        after every query.
        Restart console kernel (Ctrl+.) and reboot Opsens-PicoM to avoid
        running errors.
        Read Opsens Serial Comm. User Manual and pyVisa documentation on  
        ResourceManager class, subclass SerialInstrument 
        to initialize Opsens PicoM.
"""
 
rm = pyvisa.highlevel.ResourceManager()
opsensVisaAddress = 'ASRL3::INSTR'
opsens = rm.open_resource(opsensVisaAddress)
opsens.CR = '\r'
opsens.LF='\n'
opsens.stop_bits = constants.StopBits.one
opsens.parity = constants.Parity.none
opsens.flow_control = constants.VI_ASRL_FLOW_NONE
opsens.data_bits = 8
opsens.baud_rate = 9600

opsens.open()
print(opsens.query("system:idn?\r"))
opsens.close()

opsens.open()
opsens.query("memory:delete:all\r")
opsens.close()

"""
:First Solution
:Status: Not working
         Raises Err-202
"""
#rawData0=''
#opsens.open()
#opsens.query("memory:acquire:start "+str(ntimes)+"\r")
#time.sleep((delay*ntimes)+0.001)
#opsens.close()
#
#opsens.open()
#for x in range(ntimes):
#    rawData0+=opsens.query("memory1:download? "+str(ntimes)+",0")
#    time.sleep(delay+0.0001)
#opsens.close()
"""
:Second Solution
:Status: Not working
         Raises VisaIOError
"""
#opsens.open()
#opsens.write("measure.start "+str(ntimes)+"\r")
#time.sleep(ntimes*delay)
#rawData0 = opsens.read("measure.start "+str(ntimes)+"\r")
#opsens.query("measure:stop\r")
#opsens.close()
"""
:Third Solution
:Status: Functions but not optimally
         Raises Err-201, Err-170, Err-140
         Times may not be corresponding to temp value
         
"""
rawData0=''
opsens.open()
for i in range(ntimes):
    #20000 is arbitrary. Must be between 1-INFINITE   
    rawData0+=opsens.query("measure:start "+str(ntimes)+"\r")
    time.sleep((delay)+0.0001)
opsens.close()

data0 = rawData0.split('\n')
removeData = ['\4','\4','CH1','Err -170','Err -201','Err -140', "Err -202",""]
data1 = []

for x in range(len(data0)):
    time=x*float(delay)
    temp = "?"
    if data0[x] not in removeData:
        temp=data0[x]
    data1.append([time,temp])

for y in range(len(removeData)):
    while removeData[y] in data0:
        data0.remove(removeData[y])