# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 22:19:19 2019
:Author:   Sena Yevenyo.
:Program:  Reads data from Opsens-PicoM Sensor.
:Return:   Recorded temperatures in list [time, temp] format
           as data1.
:Return:   Recorded temperature in list [temp] format in delay*ntimes seconds
           as data0.
"""

"""
:readme: Read Opsens Serial Communication User Manual
         and pySerial documentation to set up Opsens.
         
         delay = 0.02: This value is the minimum period Opsens
         can record data. Can be changed using "Measure:run #\n"
         where # is the period in seconds
         
         removeMisc are return characters and descriptors that aren't revelant
"""

import serial

delay = 0.02;
ntimes = 1000;

ser = serial.Serial("COM3",9600, timeout=((ntimes*delay)+2))
unicodestring = "measure:start "+str(ntimes)+"\n"

ser.write(unicodestring.encode("ascii"))
rawData0 = ser.read(ntimes*10)
rawData0 = rawData0.decode("ascii")
data0 = rawData0.split('\n')

removeMisc = ['\4','CH1']
errors = ['Err -170','Err -201', 'Err -140','Err -160']
data1 = []

for y in range(len(removeMisc)):
    while removeMisc[y] in data0:
        data0.remove(removeMisc[y])

for x in range(len(data0)):
    time = x*float(delay)
    temp = "?"
    if data0[x] not in errors:
        temp=data0[x]
    data1.append([time,temp])
ser.close()