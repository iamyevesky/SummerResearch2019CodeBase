# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 11:22:07 2019

@author: yevenyos
"""

def opsensRead(numTimes):
    import serial

    delay = 0.02;
    ntimes = numTimes;

    ser = serial.Serial("COM3",9600, timeout=((ntimes*delay)+2))
    unicodestring = "measure:start "+str(ntimes)+"\n"

    ser.write(unicodestring.encode("ascii"))
    rawData0 = ser.read(ntimes*10)
    rawData0 = rawData0.decode("ascii")
    data0 = rawData0.split('\n')

    removeMisc = ['\4','CH1','']
    errors = ['Err -170','Err -201', 'Err -140','Err -160']
    data1 = []

    for y in range(len(removeMisc)):
        while removeMisc[y] in data0:
            data0.remove(removeMisc[y])
    
    for x in range(len(data0)):
        time = x*float(delay)
        temp = "?"
        if data0[x] not in errors:
            temp=float(data0[x])
        data1.append([time,temp])
    ser.close()
    return data1

