# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:59:44 2019

@author: Sena Yevenyo
@version: Semptember 24, 2019
"""
import pyvisa, time

class Oscilloscope:
    rm = pyvisa.highlevel.ResourceManager()
    def __init__(self, short_record_length, long_record_length, numchan, visa_address):
        self.data = []
        if visa_address is None:
            self.visa_address = 'USB::0x0699::0x0408::C043120::INSTR'
        else:
            self.visa_address = visa_address
        self.scope = self.rm.open_resource(self.visa_address)
        self.short_record_length = short_record_length
        self.long_record_length = long_record_length
        self.numchan = numchan
        
    def setUp(self):
        self.scope.write(":SELECT:CH1 on")
        self.scope.write(":SELECT:CH2 on")
        self.scope.write("WFMOutpre:ENCdg ASCii")
        self.scope.write('Data:width 2')
        self.scope.write(':Horizontal:Recordlength '+str(self.long_record_length))
        
        
    def checkscale(self, numchan):
        self.scope.write(':Horizontal:Recordlength '+str(self.short_record_length))
        hScale = 1*10^(-9)*self.short_record_length
        self.scope.write(":Horizontal:Scale "+str(hScale))
        self.scope.write('DATA:START 1')
        self.scope.write('DATA:STOP '+str(self.short_record_length))
        self.scope.write('ACQUIRE:STOPAFTER RUnsTOP')
        
        for i in range(numchan):
            okayscale = 0
            while okayscale == 0:
                channel = i+1
                self.__set_channel(channel)
                okayscale = self.__setScale(self.__withinRange(self.__getRawData()), channel)
    
    def __getRawData(self):
        return self.scope.query_ascii_values("CURVE?")
    
    def __get_dt(self):
        return float(self.scope.query('WFMOutpre:XINCR?'))

    def __set_channel(self, channel):
        self.scope.write(":DATa:SOUrce CH"+str(channel))
        
    def __calc_wait_time(self):
        dt = self.__get_dt()
        return self.long_record_length*dt
    
    def __getVoltageData(self):
        #Query returns the y-axis scale on oscilloscope graph
        ymult = float(self.scope.query('WFMOutpre:YMULT?'))
        #Query returns the y-zero value of the oscilloscope graph
        yzero = float(self.scope.query('WFMOutpre:YZERO?'))
        #Query returns the offset value for the y-axis on the oscilloscope graph
        yoff = float(self.scope.query('WFMOutpre:YOFF?'))
        
        raw_data = self.__getRawData()
        npoint=len(raw_data)
        voltage=[]
        for i in range(npoint):
            voltage.append(ymult*(raw_data[i]-yoff)+yzero)
        return voltage
    
    def __get_time(self):
        times=[]
        xincr = float(self.scope.query('WFMOutpre:XINCR?'))
        for i in range(self.record_length):
            times.append(float(i)*xincr)
        return times
    
    def __withinRange(self,data):
        highcount = 0
        lowcount = 0
        if( max(data)<=32767.0/2.0 or min(data)>=-32767.0/2.0):
            lowcount = 1;
        
        for j in range(self.short_record_length):
             if ((data[j]>=32767.0) or (data[j]<=-32767.0)): #Why 32760?
                 highcount += 1
        if highcount/(float(self.short_record_length)) > 0.0001:
            return -1
        elif lowcount>0:
            return 1
        return 0
    
    def __setScale(self, value, channel):
        chscale = float(self.scope.query("CH"+str(channel)+":SCALE?"))
        output = 0
        newchscale = chscale
        
        if value == 1:
            if chscale in [0.001, 0.01, 0.1, 1.0, 0.005, 0.05, 0.5, 5.0]:
                newchscale = chscale*2
            elif chscale in [0.002, 0.02, 0.2, 2.0]:
                newchscale = chscale*2.5
            elif chscale == 10:
                output = 1
                print('CH'+str(channel)+': already at max scale')
        
        elif value == -1:
            if chscale in [0.01, 0.1, 1.0, 10.0, 0.002, 0.02, 0.2, 2.0]:
                newchscale = chscale/2
            elif chscale in [ 0.005, 0.05, 0.5, 5.0]:
                newchscale = chscale/2.5
            elif chscale == 0.001:
                output = 1
                print('CH'+str(channel)+': already at min scale')
        
        elif value == 0:
            output = 1;
        
        self.scope.write("CH"+str(channel)+":SCALE "+str(newchscale))
        print('CH'+str(channel)+': changing scale from '+str(chscale)+' to '+str(newchscale))
        return output
        
    def __readVoltageData(self,numchan):
         wait_time = self.__calc_wait_time();
         self.scope.write('DATA:START 1')
         self.scope.write('DATA:STOP '+str(self.long_record_length))
         self.scope.write('acquire:stopafter sequence')
         voltage = [['?']*(self.long_record_length)]*numchan
         
         for i in range(numchan):
             self.__set_channel(i+1)
             voltage[i]=self.__getVoltageData()                
             time.sleep(wait_time)
         
         self.scope.write('FPAnel:PRESS runstop')
         output = [self.__get_time()]
         for i in range(numchan):
             output+=[voltage[i]]
         self.scope.close()
         return output
     
    def recordData(self):
        self.data = self.__readVoltageData(self.numchan)
    
    def getData(self):
        return self.data
    

#import Oscilloscope, Opsens
longRecordLength = 100000
shortRecordLength = 10000
numberOfChan = 3
numOfDataPointsTherm = 10000

scope = Oscilloscope(shortRecordLength, longRecordLength, numberOfChan, None);
scope.setUp()
#scope.checkscale(2)
scope.recordData()
data = scope.getData()
print(data)