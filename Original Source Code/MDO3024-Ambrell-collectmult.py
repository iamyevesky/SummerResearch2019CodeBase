import os
import sys
import numpy
import math
import scipy
import time
import visa
from time import gmtime, strftime
import pandas as pd
import matplotlib.pyplot as plt
import zoefavs as z


pi = math.pi 
inf = numpy.inf





short_record_length = 10000
long_record_length = 1000000
descriptor = 'CH1-Hcoil-CH2-Mcoil-LiquidResearch-in-epoxy-June-2019'
numcollects = 15
numchan=2
pause = 0
#note time between data collections is about 16 seconds already because of various oscilloscope data transfer wait times
#(which are probably overly conservative)
#so any nonzero pause value makes that wait time longer than 16 seconds.





def writefunc(k):
    if k % 10 == 0:
    #if (k >= start1 and k <= stop1) or (k >= start2 and k <= stop2) or (k >= start3 and k <= stop3):
        return 1
    else:
        return 0

#define multiplier (e.g. +1 or -1 depending on polarity)
#this is polarity like if one of the channels is inverted wrt the other
polarity = 1

#does g factor make phase difference a lead or lag?
phase_sign = -1




os.chdir(r'''C:\Research\data\TektronixMDO3024''')

import MDO3024collectdataforAmbrell

#visa_address = 'TCPIP::169.254.3.117::INSTR'
#visa_address = 'USB::0x0699::0x0408::C043120::INSTR'

#opsens_visa_address = 'ASRL5::INSTR'


    
#rm = visa.ResourceManager()

#opsens = rm.open_resource(opsens_visa_address, baud_rate = 9600, data_bits = 8, write_termination= '\r', read_termination = '\4\n')
#print(opsens.query("*IDN?"))

#scope = rm.open_resource(visa_address)
#print(scope.query("*IDN?"))





print('Starting...')
#print('Check oscilloscope V/div at max and min frequencies.')
print('Set oscilloscope Run/Stop button to GREEN.')
#qproceed = input("Press any key when you are ready to continue, or type quit to quit.")

#if qproceed == 'quit':
#    sys.exit()

nstart = 0


for j in range(numcollects):
    if nstart ==0:
        timesubf = strftime("%H%M%S")
    (nstart, outdir) = MDO3024collectdataforAmbrell.mainforAmbrell(numchan, timesubf, nstart, descriptor, j, short_record_length, long_record_length)
    print(outdir)
    print('nstart = '+str(nstart))
    time.sleep(pause)
    