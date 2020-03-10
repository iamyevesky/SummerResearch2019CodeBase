# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 12:45:45 2019

@author: yeves
"""

import time
import pyvisa
import serial

"""
:brief Converts list data from scope to voltage values 
:param list data type raw_rata contains the values recorded
:from scope in ASCII format
:param  resourceManager object scope: access point of the oscilloscope
:return list data type voltage: recorded voltage values
"""
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
"""
:brief sets the channel of the scope
:param  resourceManager object scope: access point of the oscilloscope
:param int data type channel: channel scope is to be set
"""
def set_channel(scope, channel):
    scope.write(":DATa:SOUrce CH"+str(channel))
"""
:brief obtains raw data from oscilloscope and converts it into voltage list
:param  resourceManager object scope: access point of the oscilloscope
:return list data type voltage: recorded voltage values
"""
def get_data(scope):
    scope.write("WFMOutpre:ENCdg ASCii")
    data = scope.query_ascii_values("CURVE?")
    voltage=convert_raw_voltage_data(data, scope)
    return voltage

"""
:brief prints recorded data into datasheet docuement with corresponding
 voltage and time recorded from each of the channels
:param  resourceManager object scope: access point of the oscilloscope
:param int data type numchan is number of channels
:param list data type voltage contains recorded voltage values
:param list data type times contains recorded time values corresponding
:with recorded voltage
:param float data type dt records the sampling time interval
:param file data type outfile: datasheet into which data would be stored 
:param stime data type String:Locale’s appropriate date and time representation
 param float data type timeins: time as a floating point number expressed in seconds since the epoch, in UTC.
""" 
"""
:brief obtains the times for which sampling data was recorded
:param  resourceManager object scope: access point of the oscilloscope
:param int data type record_length: number of sample data recorded
:return list data type times: the times at which sampling data was recorded
""" 
def get_time(scope, record_length):
    times=['?']*record_length
    xincr = float(scope.query('WFMOutpre:XINCR?'))
    print('xincr= '+str(xincr))
    for i in range(record_length):
        times[i]=float(i)*xincr
    return times  

"""
:brief obtains the recording time interval
:param  resourceManager object scope: access point of the oscilloscope
:return float data type xincr: the sampling time interval
""" 
def get_dt(scope):
    xincr = float(scope.query('WFMOutpre:XINCR?'))
    return xincr
"""
:brief obtains the total time for which data was recorded from oscillopscope
:param  resourceManager object scope: access point of the oscilloscope
:return float data type wait_time: total time taken for data sample collection
"""
def calc_wait_time(scope):
    record_length=float(scope.query(':HORIZONTAL:RECORDLENGTH?'))
    dt=get_dt(scope)
    wait_time=record_length*dt
    return wait_time

"""
:brief sets the scale for the graph of the data
:param  resourceManager object scope: the access point of the oscilloscope
:param int data type numchan: number of channels 
:param int data type short_record_length: unexplained
:param int data type long_record_length: unexplained
"""
def checkscale(scope, numchan, short_record_length, long_record_length):
    base_record_length=int(scope.query(':HORIZONTAL:RECORDLENGTH?')) 
    if short_record_length != base_record_length:
        scope.write(':Horizontal:Recordlength '+str(short_record_length)) #Why?
    hscale = 0.000000001*short_record_length*0.1 #Why?
    scope.write(":Horizontal:Scale "+str(hscale))
    #Sets the "from" part of the waveform to be captured. In this case from data point 1
    scope.write('DATA:START 1')
    #Sets the "to" part of the waveform to be captured. In this case to the last recordrd data point
    scope.write('DATA:STOP '+str(short_record_length))
    scope.write('ACQUIRE:STOPAFTER RUnsTOP')
    for i in range(numchan):
        okayscale = 0
        while okayscale == 0:
            set_channel(scope, i+1)
            scope.write("WFMOutpre:ENCdg ASCii")
            data = scope.query_ascii_values("CURVE?")
            highcount = 0
            lowcount = 0
            for j in range(short_record_length):
                if data[j] > 32760: #Why 32760?
                    highcount += 1
                elif data[j] < 32760/5:
                    lowcount += 1
            if highcount/short_record_length > 0.0001:
                chscale = float(scope.query("CH"+str(i+1)+":SCALE?"))
                """
                Oscilloscope has scales of 1mV, 2mV, 5mV, 0.1V, 0.2V, 0.5V up
                to 10V in a pattern of 1,2,5.
                To increase scale when it is a unit value of 1 or 5, multiply by 2
                else multiply by 2.5.
                If scale is at 10V, then that is the max.
                """
                if chscale in [0.001, 0.01, 0.1, 1.0, 0.005, 0.05, 0.5, 5.0]:
                    newchscale = chscale*2
                if chscale in [0.002, 0.02, 0.2, 2.0]:
                    newchscale = chscale*2.5
                if chscale == 10:
                    okayscale = 1
                    print('CH'+str(i+1)+': already at max scale')
                    break                    
                scope.write("CH"+str(i+1)+":SCALE "+str(newchscale))
                print('CH'+str(i+1)+': changing scale from '+str(chscale)+' to '+str(newchscale))
            if lowcount/short_record_length > 0.9999 and highcount/short_record_length < 0.0001:
                chscale = float(scope.query("CH"+str(i+1)+":SCALE?"))
                if chscale in [0.01, 0.1, 1.0, 10.0, 0.002, 0.02, 0.2, 2.0]:
                    newchscale = chscale/2
                if chscale in [ 0.005, 0.05, 0.5, 5.0]:
                    newchscale = chscale/2.5
                if chscale == 0.001:
                    okayscale = 1
                    print('CH'+str(i+1)+': already at min scale')
                    break                     
                scope.write("CH"+str(i+1)+":SCALE "+str(newchscale))
                print('CH'+str(i+1)+': changing scale from '+str(chscale)+' to '+str(newchscale))
            if highcount/short_record_length < 0.0001 and lowcount/short_record_length < 0.9999:
                okayscale = 1
        scope.write(":Horizontal:recordlength "+str(long_record_length))
        hscale = 0.000000001*long_record_length*0.1
        scope.write(":Horizontal:Scale "+str(hscale))

"""
:brief reads data from oscilloscope and returns recorded voltage
:param resourceManager object scope: the access point of the oscilloscope 
:param int data type numchan: number of channels 
:param int data type nstart: unexplained
:param String data type descriptor: describes the experiment undertaken
:param int data type short_record_length: unexplained
:param int data type long_record_length: unexplained
"""
def read_and_write_data_from_Nch(scope, numchan, nstart, short_record_length, long_record_length):
    checkscale(scope, numchan, short_record_length, long_record_length)    
    wait_time = calc_wait_time(scope)
    record_length=int(scope.query(':HORIZONTAL:RECORDLENGTH?'))
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
    scope.close()
    return output

"""
:brief plots the data received from oscilloscope
:param resourceManager object scope: the access point of the oscilloscope 
:param int data type nstart: unexplained
:param int data type i: channel from which data is read
:param list data type times: the times at which sampling data was recorded
:param list data type voltage: recorded voltage values
:param String data type figoutfile: adress where graphs plotted are stored
:param String data type descriptor: describes the experiment undertaken
:return
"""
"""
:brief
:param
:param
:return
"""
def mainforAmbrell(numchan, nstart, j, short_record_length, long_record_length):
    
    #Initialize system for data-taking
    rm = pyvisa.highlevel.ResourceManager()
    #Visa address for Tektronik Osciloscope
    visa_address = 'TCPIP::169.254.3.117::INSTR'

    scope = rm.open_resource(visa_address)
    #Open channels
    scope.write(":SELECT:CH1 on")
    scope.write(":SELECT:CH2 on")
    scope.write(":SELECT:CH3 on")
    #Encodes oscilloscope data into ASCII format
    scope.write(":DATA:ENCDG ASCII")
    
    scope.write('Data:width 2')
    
    return read_and_write_data_from_Nch(scope, numchan, nstart, short_record_length, long_record_length)

def scopeRead(shortRecordLength, longRecordLength, numCollects, numChan):
    short_record_length = shortRecordLength
    long_record_length = longRecordLength
    #descriptor = 'CH1-Hcoil-CH2-Mcoil-empty-test'
    numcollects = numCollects
    numchan= numChan
    
    """
    note time between data collections is about 16 seconds already because of various oscilloscope data transfer wait times
    (which are probably overly conservative)
    so any nonzero pause value makes that wait time longer than 16 seconds
    """
    pause = 0
    nstart = 0
    output = []
    
    for j in range(numcollects):
        output += [mainforAmbrell(numchan, nstart, j, short_record_length, long_record_length)]
        time.sleep(pause)
    
    return output

def opsensRead(numTimes):
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