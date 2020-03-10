# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 17:30:05 2019

@author: yevenyos
"""

import time
import pyvisa
import serial
import csv
from pathlib import Path
import os
import xlsxwriter


rm = pyvisa.highlevel.ResourceManager()
#Visa address for Tektronik Osciloscope
visa_address = 'USB::0x0699::0x0408::C043120::INSTR'
scope = rm.open_resource(visa_address)
#Open channels
scope.write(":SELECT:CH1 on")
scope.write(":SELECT:CH2 on")
#Encodes oscilloscope data into ASCII format
scope.write(":DATA:ENCDG ASCII")
scope.write('Data:width 2')
avgTimeDataCollect = [[] for i in range(100)]
avgTimeCheckscale = []
meanTimeDataCollect = []

def read_and_write_data_from_Nch(scope, numchan, nstart, short_record_length, long_record_length):    
    record_length = long_record_length
    wait_time = calc_wait_time(scope)
    scope.write('DATA:START 1')
    scope.write('DATA:STOP '+str(record_length))
    scope.write('acquire:stopafter sequence')
    voltage = [['?']*(record_length)]*numchan
    for i in range(numchan):
        set_channel(scope, i+1)
        voltage[i]=get_data(scope)                
        time.sleep(wait_time)
    set_channel(scope, 1)
    times=get_time(scope, record_length)
    scope.write('FPAnel:PRESS runstop')
    
    output = [times]
    for i in range(numchan):
        output+=[voltage[i]]
    
    return output

def calc_wait_time(scope):
    record_length=float(scope.query(':HORIZONTAL:RECORDLENGTH?'))
    dt=get_dt(scope)
    wait_time=record_length*dt
    return wait_time

def get_time(scope, record_length):
    times=['?']*record_length
    xincr = float(scope.query('WFMOutpre:XINCR?'))
    print('xincr= '+str(xincr))
    for i in range(record_length):
        times[i]=float(i)*xincr
    return times

def set_channel(scope, channel):
    scope.write(":DATa:SOUrce CH"+str(channel))

def get_data(scope):
    scope.write("WFMOutpre:ENCdg ASCii")
    data = scope.query_ascii_values("CURVE?")
    voltage=convert_raw_voltage_data(data, scope)
    return voltage

def getRawData(scope):
    return scope.query_ascii_values("CURVE?")

def setScale(scope, value, channel):
    chscale = float(scope.query("CH"+str(channel)+":SCALE?"))
    output = 0
    newchscale = chscale
        
    if value == -1:
        if chscale in [0.001, 0.01, 0.1, 1.0, 0.005, 0.05, 0.5, 5.0]:
            newchscale = chscale*2
        elif chscale in [0.002, 0.02, 0.2, 2.0]:
            newchscale = chscale*2.5
        elif chscale == 10:
            output = 1
            print('CH'+str(channel)+': already at max scale')
        
    elif value == 1:
        if chscale in [0.01, 0.1, 1.0, 10.0, 0.002, 0.02, 0.2, 2.0]:
            newchscale = chscale/2
        elif chscale in [ 0.005, 0.05, 0.5, 5.0]:
            newchscale = chscale/2.5
        elif chscale == 0.001:
            output = 1
            print('CH'+str(channel)+': already at min scale')
        
    elif value == 0:
        output = 1;
        
    scope.write("CH"+str(channel)+":SCALE "+str(newchscale))
    print('CH'+str(channel)+': changing scale from '+str(chscale)+' to '+str(newchscale))
    return output

def withinRange(short_record_length,data):
    #1.02396875
    highcount = 0
    lowcount = 0
    if( max(data)<=32767.0/2 or min(data)>=-32767.0/2):
        lowcount = 1;
        
    for j in range(short_record_length):
        if ((data[j]>=32767.0) or (data[j]<=-32767.0)): #Why 32760?
            highcount += 1
    if float(highcount)/(float(short_record_length)) > 0.0001:
        return -1
    elif lowcount>0:
        return 1
    return 0

def get_dt(scope):
    xincr = float(scope.query('WFMOutpre:XINCR?'))
    return xincr

def convert_raw_voltage_data(raw_data, scope):
    #Query returns the y-axis scale on oscilloscope graph
    ymult = float(scope.query('WFMOutpre:YMULT?'))
    #Query returns the y-zero value of the oscilloscope graph
    yzero = float(scope.query('WFMOutpre:YZERO?'))
    #Query returns the offset value for the y-axis on the oscilloscope graph
    yoff = float(scope.query('WFMOutpre:YOFF?'))
    npoint=len(raw_data)
    voltage=['?']*npoint
    #Convert raw data values and fill into voltage list
    #Non-recorded data appears as '?' in voltage list
    for i in range(npoint):
        voltage[i]=ymult*(raw_data[i]-yoff)+yzero
    return voltage

def checkscale(scope, numchan, short_record_length, long_record_length):
    scope.write(':Horizontal:Recordlength '+str(short_record_length))
    scope.write('DATA:START 1')
    scope.write('DATA:STOP '+str(short_record_length))
    scope.write('ACQUIRE:STOPAFTER RUnsTOP')
    
    for i in range(numchan):
        okayscale = 0
        while okayscale == 0:
            channel = i+1
            set_channel(scope,channel)
            okayscale = setScale(scope, withinRange(short_record_length,getRawData(scope)), channel)

def addDirectory(iPath, newPath):
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    return iPath+'\\'+newPath

for i in range(100):
    for j in range(20):
        startTime = time.time()
        read_and_write_data_from_Nch(scope, 2, 0, 0, (i+1)*1000)
        endTime = time.time()
        avgTimeDataCollect[i].append(endTime-startTime)
    meanTimeDataCollect.append(sum(avgTimeDataCollect[i])/float(len(avgTimeDataCollect[i])))
        
#for i in range(20):
#    startTime = time.time()
#    checkscale(scope, 2, 10000, 100000)
#    endTime = time.time()
#    avgTimeCheckscale.append(endTime-startTime)
excelFilePath = "C:\\Users\\yevenyos\\Desktop"
excelFilePath = addDirectory(excelFilePath,"SynchronousTestData2.xlsx")
workbook = xlsxwriter.Workbook(excelFilePath)
worksheet = []
worksheet.append(workbook.add_worksheet("ReadWriteDataPointsTime"))
worksheet.append(workbook.add_worksheet("AverageReadWrite"))
#worksheet.append(workbook.add_worksheet("CheckscaleTime"))

for i in range(100):
    worksheet[0].write(0,i,(i+1)*1000)
    for j in range(20):
        worksheet[0].write((j+1),i,avgTimeDataCollect[i][j])

for i in range(100):
    worksheet[1].write(i,0,(i+1)*1000)
    worksheet[1].write(i,1,meanTimeDataCollect[i])
    
#for i in range(20):
#    worksheet[2].write(i,0,avgTimeCheckscale[i])
workbook.close()