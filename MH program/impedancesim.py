# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:05:26 2019

@author: boekelhz
"""
#import xlrd
#import os
#import xlsxwriter
#import cmath
#import scipy
import numpy as np
#from scipy.optimize import curve_fit
#import os
#import matplotlib.pyplot as plt
#import pandas as pd

#numlumps = 4



#C = 70e-12
#L = 800e-9
#R1 = 11.0
#R2 = 25.0





def impedance(C, L, R1, R2, BNClen, numlumps, f0, fmax, numf):
    #numlumps = np.int(numlumps)

    numeqns = (numlumps+1)*3
    #numf=1000
    
    CBNC = 100e-12*BNClen/4

    
    LBNC = 250e-9*BNClen/4
    
    #RBNC = 0.1*BNClen/4

    Ia = 1.0

    
    flist = numf*[0.0]
    
    xlist = numf*[numeqns*[0.0]]
    
    vmaglist = [0.0]*numf
    
    vphaselist = [0.0]*numf
    
    vlist = [0.0]*numf
    
    for i in range(numf): 
        flist[i] = f0 + ((fmax-f0)/numf)*i

        w = 2 * np.pi * flist[i]
        

        ZC = 1/(1.0j*w*(CBNC/numlumps))

        ZL = 1.0j*w*(LBNC/numlumps)

        
        #a = np.array([[1,0,0,0,0,0],[1,2,3,0,0,0],[0,0,1,-1,-1,-1],[0,0,0,0,2,2],[1,2,3,4,5,6],[1,2,6,5,4,3]])
        #a = np.array([[1,0,-1/(1.0j * w * CBNC),0,0,0],[1,-1,0,-(1.0j w *LBNC + RBNC),0,0],
        a = np.array(numeqns*[numeqns*[0.0j]])
        
        b = np.array(numeqns*[0.0j])
        b[0] = Ia
        
        a[0,0] = 1
        a[0,1] = 1
        for j in range(numlumps):
            k = j+1
            l = 2*j+1
            a[k,l] = -1.0+0.0j
            a[k, l+1] = 1.0+0.0j
            a[k, l+2] = 1.0+0.0j
        for j in range(numlumps):
            k = j+numlumps+1
            l = j+2*numlumps+2
            a[k, 2*j] = -ZC
            a[k, l] = 1.0+0.0j
        for j in range(numlumps):
            k = j+2*numlumps+1
            l = j+2*numlumps+2
            a[k, 2*j+1] = -ZL
            a[k, l] = 1.0+0.0j       
            a[k, l+1] = -1.0+0.0j
            
        a[3*numlumps+1, 2*numlumps] = -(1/(1.0j*w*C) + R2)
        a[3*numlumps+1, 3*numlumps+2]=1
        a[3*numlumps+2, 2*numlumps+1] = -(1.0j *w*L + R1)
        a[3*numlumps+2, 3*numlumps+2]=1    
        #print(a)
        
        x = np.linalg.solve(a, b)
        
        #print(x)
        xlist[i] = x
        #v1 = x[2*numlumps+2]
        v1mag = np.abs(x[2*numlumps+2])
        vmaglist[i] = v1mag
        v1phase = np.angle(x[2*numlumps+2])
        vphaselist[i] = v1phase
        vlist[i] = x[2*numlumps+2]
        
    #return (flist, vmaglist, vphaselist)
    return([flist, vmaglist, vphaselist])





'''
plt.plot(flist, vmaglist)
#plt.plot(wlist, vphaselist)

#print(flist[100], vlist[100])
#print(flist[400], vlist[400])
'''

#os.chdir(r'''C:\Users\boekelhz\a1Lafayette\data\RandSZND''')


'''
simfilenm = "sim-test-compare-to-analytical-sol.txt-formatted.csv"
simfile = simfilenm
simdata = pd.read_csv(simfile)
simfreq = flatten(simdata.iloc[:,0:1].values.tolist())
simreal = flatten(simdata.iloc[:,1:2].values.tolist())
simimag = flatten(simdata.iloc[:,2:3].values.tolist())

simmag  = [0.0]*len(simfreq)
simphase  = [0.0]*len(simfreq)
for i in range(len(simfreq)):
    simfreq[i] = float(simfreq[i])
    simreal[i] = float(simreal[i])
    simimag[i] = float(simimag[i])
    simmag[i] = np.abs(complex(simreal[i], simimag[i]))
    simphase[i] = np.angle(complex(simreal[i], simimag[i]))

#plt.title('Impedance')
plt.grid(True)
plt.ylabel('Impedance (Ohms)')
plt.xlabel('frequency (Hz)')
plt.plot(simfreq, simmag, label=r'5SPICE w 4 BNC lump')
plt.plot(flist, vmaglist, label=r'analytic sol w 200 BNC lump')

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
'''