# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
def vnaRead():
    import pyvisa
    import time
    startFreq = 100e3
    endFreq = 30e6
    measuredValue = "'Z-S11'"
    trace = "'Trc1'"
    
    rm = pyvisa.highlevel.ResourceManager()
    visaAddress = 'TCPIP::139.147.54.111::inst0::INSTR'
    
    vna = rm.open_resource(visaAddress)
    vna.write_termination = '\r'
    vna.read_termination = '\n'
    vna.write('*rst')
    vna.write('display:window1:state on')
    vna.write('calculate:format mlinear')
    vna.write('sense1:sweep:points 5001')
    delay = vna.query('sense1:sweep:time?')
    print(delay)
    vna.write("calculate1:parameter:measure "+trace+", "+measuredValue)
    vna.write('sense1:frequency:start '+str(startFreq)+';stop '+str(endFreq))
    time.sleep(1)
    vna.write("display:window1:trace1:y:scale:auto once, "+trace)
    csv = vna.query('calculate1:data? fdata')
    time.sleep(float(delay))
    meas = csv.split(',')
    freq = ['?']*len(meas)
    
    for i in range(len(meas)):
        freq[i] = startFreq+((endFreq-startFreq)/float(len(meas)))*i
        meas[i] = float(meas[i])
    
    meas = [freq]+[meas]
    return meas

answer = vnaRead()