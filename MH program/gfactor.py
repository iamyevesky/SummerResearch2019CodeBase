# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:05:26 2019

@author: boekelhz
"""
#import xlrd
import os, csv
#import xlsxwriter
#import cmath
#import scipy
import numpy as np
#import matplotlib.pyplot as plt
#import pandas as pd

#numlumps = 4



#C = 70e-12
#L = 800e-9
#R1 = 11.0
#R2 = 25.0


'''
def flatten(l):
  out = []
  for item in l:
    if isinstance(item, (list, tuple)):
      out.extend(flatten(item))
    else:
      out.append(item)
  return out
'''
def gfactor(C, L, R1, R2, BNClen, numlumps, f0, fmax, numf, Rosc, path, dattimestring):
    #numlumps = np.int(numlumps)
    
    numeqns = (numlumps+1)*3
    #numf=1000
    
    CBNC = 100e-12*BNClen/4
    
    LBNC = 250e-9*BNClen/4
    
    #RBNC = 0.1*BNClen/4

    VM = 1.0

    
    flist = numf*[0.0]
    
    xlist = numf*[numeqns*[0.0]]
    
    vmaglist = [0.0]*numf
    
    vphaselist = [0.0]*numf
    
    vlist = [0.0]*numf
    
    gmag = [0.0]*numf

    gphase = [0.0]*numf
    
    greal = [0.0]*numf
    
    gimag = [0.0]*numf
    
    for i in range(numf):
        f = f0 + ((fmax-f0)/numf)*i
        flist[i] = f
        w = 2 * np.pi * f
        
        ZC = 1/(1.0j*w*(CBNC/numlumps))
        ZL = 1.0j*w*(LBNC/numlumps)
        
        
        #a = np.array([[1,0,0,0,0,0],[1,2,3,0,0,0],[0,0,1,-1,-1,-1],[0,0,0,0,2,2],[1,2,3,4,5,6],[1,2,6,5,4,3]])
        #a = np.array([[1,0,-1/(1.0j * w * CBNC),0,0,0],[1,-1,0,-(1.0j w *LBNC + RBNC),0,0],
        a = np.array(numeqns*[numeqns*[0.0j]])
        
        b = np.array(numeqns*[0.0j])
        b[3*numlumps+2] = VM
        
        a[0,0] = 1.0
        a[0,1] = 1.0
        a[0,numlumps*2+2] = 1.0/Rosc
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
        a[3*numlumps+1, 3*numlumps+2]=1.0
        a[3*numlumps+2, 2*numlumps+1] = -(1.0j*w*L + R1)
        a[3*numlumps+2, 3*numlumps+2]=1.0 
        
        x = np.linalg.solve(a, b)
        
        #print(x)
        xlist[i] = x
        v1 = x[2*numlumps+2]
        v1mag = np.abs(x[2*numlumps+2])
        vmaglist[i] = v1mag
        v1phase = np.angle(x[2*numlumps+2])
        vphaselist[i] = v1phase
        vlist[i] = x[2*numlumps+2]
        gmag[i] = np.abs(1/v1)
        gphase[i] = np.angle(1/v1)
        greal[i] = np.real(1/v1)
        gimag[i] = np.imag(1/v1)
        
    #Write to .csv file
    os.chdir(path)

    outfile = dattimestring+"gfactors.csv"
    if os.path.exists(outfile):
        os.remove(outfile)    
        
    formattedfile=open(outfile, 'a')

    formattedfile.write('Frequency (Hz), gfactor magnitude, gfactor phase, gfactor real component, gfactor imaginary component \n')
    for i in range(len(flist)):
        formattedfile.write(str(flist[i])+',')
        formattedfile.write(str(gmag[i])+',')
        formattedfile.write(str(gphase[i])+',')
        formattedfile.write(str(greal[i])+',')
        formattedfile.write(str(gimag[i])+',')
        formattedfile.write('\n')
    formattedfile.close()
        
        
    #return (flist, vmaglist, vphaselist)
    return([flist, gmag, gphase, greal, gimag])
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

def readGFactorData(date, time, filepath, coil):
    filepath = addDirectory(filepath, date)
    filepath = addDirectory(filepath, time)
    filepath = addDirectory(filepath, coil)
    filepath = addDirectory(filepath, date+time+'gfactors.csv')
    
    with open(filepath, 'r', newline ='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter = ',')
        csvreaderlist = []
        for row in csvreader:
            csvreaderlist.append(row)
        freq = []
        gfactormag = []
        gfactorphase = []
        for i in range(1,len(csvreaderlist)):
            freq.append(float(csvreaderlist[i][0]))
            gfactormag.append(float(csvreaderlist[i][1]))
            gfactorphase.append(float(csvreaderlist[i][2]))
    output = [(freq,gfactormag),(freq,gfactorphase)]
    
    return output
def addDirectory(iPath, newPath):
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    return iPath+'\\'+newPath