# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 14:16:03 2019

@author: yeves
"""
import Oscilloscope, Opsens
longRecordLength = 100000
shortRecordLength = 10000
numberOfChan = 3
numOfDataPointsTherm = 10000

scope = Oscilloscope(shortRecordLength, longRecordLength, numberOfChan);
therm = Opsens(numOfDataPointsTherm)

scope.setUp()
scope.checkscale()
scope.recordData()
data = scope.getData()
print(data)

therm.recordData()
therm.getData()
