# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 01:17:39 2019

@author: yeves
"""
import serial

class Opsens:
    #Frequency of data collected is 50Hz
    freq = 50.0
    
    
    def __init__(self, numCollects, port):
        self.data=[]
        self.numCollects = numCollects
        if port is None:
            self.port = "COM3"
        else:
            self.port = port
        self.ser = serial.Serial("COM3",9600, timeout=(self.numCollects/self.freq))
    
    def recordData(self):
        rawData = self.ser.read(self.numCollects).decode("ascii")
        self.data = rawData.split('\n')
        
    def getData(self):
        return self.data