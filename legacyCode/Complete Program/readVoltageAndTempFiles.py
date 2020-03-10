# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:06:03 2019

@author: yeves
"""

import csv
from pathlib import Path
import os

def readVoltageData(filepath, date, time, numCollects, numChan):
    filepath = addDirectory(filepath, date)
    filepath = addDirectory(filepath, time)
    filepath = addDirectory(filepath, 'Oscilloscope')
    
    output = [[] for i in range(numChan)]
    for i in numCollects:
        time = []
        voltage = [[] for range in numChan]
        voltageFilepath = addDirectory(filepath, 'voltageDataScopeRun'+date+time+'('+str(i+1)+').csv')
        with open(voltageFilepath, 'r', newline = '') as csvfile:
            csvreader = csv.reader(csvfile, delimiter = ',')
            for j in range(len(csvreader)):
                time.append(csvreader[j+1][0])
                for k in numChan:
                    voltage[k].append(csvreader[j+1][k+1])
        for l in range(numChan):
            output[l].append((time,voltage[l]))
     
    return output           

def readTempData(filepath, date, time, numCollects):
    """
    Delay is the amount of time taken for Opsens to record data
    for each data point.
    It takes the oscilloscope an average of 1.6 - 1.7 seconds for every run
    We decide on 1.8 seconds for each run because time is also needed for
    writing things ex cetera.
    Hence the value of 1.
    """
    
    delay = 0.02;
    dataPointsForEachScopeRun = int(1.80/delay)
    filepath = addDirectory(filepath, date)
    filepath = addDirectory(filepath, time)
    filepath = addDirectory(filepath, 'Opsens')
    tempFilepath = addDirectory('tempData'+date+time+'.csv')
    output = ['*']*numCollects
    
    with open(tempFilepath, 'r', newline = '') as csvfile:
        csvreader = csv.reader(csvfile, delimiter = ',')
        index = 0
        for i in range(len(output)):
            indexRange = dataPointsForEachScopeRun+index
            times = []
            temp = []
            for j in range(index,indexRange):
                times.append(csvreader[j][0]) 
                temp.append(csvreader[j][1])
            output[i] = (times,temp)
            index+=dataPointsForEachScopeRun
    
    return output

def addDirectory(iPath, newPath):
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    return iPath+'\\'+newPath