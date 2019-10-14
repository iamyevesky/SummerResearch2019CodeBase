# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 09:40:31 2019

@author: boekelhz
"""

# <examples/doc_fitting_withreport.py>
import numpy as np
import lmfit
import matplotlib.pyplot as plt
import os
import pandas as pd
from numpy import exp, linspace, pi, random, sign, sin
from lmfit import Parameters, fit_report, minimize

'''
def flatten(l):
  out = []
  for item in l:
    if isinstance(item, (list, tuple)):
      out.extend(flatten(item))
    else:
      out.append(item)
  return out

p_true = Parameters()
p_true.add('C', value=6.24e-11)
p_true.add('L', value=0.753e-6)
p_true.add('R1', value=1.1e1)
p_true.add('R2', value=14.0e0)
'''

def residual(pars, f, data=None):
    vals = pars.valuesdict()
    C = vals['C']
    L = vals['L']
    R1 = vals['R1']
    R2 = vals['R2']

    BNClen = 4
    numlumps = 10
    numeqns = (numlumps+1)*3
    #numf=1000
    
    CBNC = 100e-12*BNClen/4
    #print('CBNC = ')
    #print(CBNC)
    
    LBNC = 250e-9*BNClen/4
    
    #RBNC = 0.1*BNClen/4

    Ia = 1.0

    #if abs(shift) > pi/2:
    #    shift = shift - sign(shift)*pi
    v1mag = [0.0]*len(f)
    v1phase = [0.0]*len(f)
    for i in range(len(f)):
        w = 2 * np.pi * f[i]
        ZC = 1/(1.0j*w*(CBNC/numlumps))
        ZL = 1.0j*w*(LBNC/numlumps)
    
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
            
        x = np.linalg.solve(a, b)
        
    
        v1mag[i] = np.abs(x[2*numlumps+2])
        v1phase[i] = np.angle(x[2*numlumps+2])
    
    #model = [v1mag, v1phase]
    if data is None:
        return [v1mag, v1phase]
    diff = [0.0]*len(f)
    for i in range(len(diff)):
        diff[i] = v1mag[i] - data[i]
    return diff


n = 1001
fmin = 1e5
fmax = 3e7

#random.seed(0)

#noise = random.normal(scale=0.7215, size=n)
#x = linspace(xmin, xmax, n)
#data = residual(p_true, x) + noise


#os.chdir(r'''C:\Users\boekelhz\a1Lafayette\data\RandSZND\20180621-Mcoil''')
'''
datfile = '20180621-Mcoil.csv'
datdata = pd.read_csv(datfile)
datfreq = flatten(datdata.iloc[:,0:1].values.tolist())
datreal = flatten(datdata.iloc[:,1:2].values.tolist())
datimag = flatten(datdata.iloc[:,2:3].values.tolist())
datmag = [0.0]*len(datreal)
datphase = [0.0]*len(datreal)


simmag  = [0.0]*len(datfreq)
simphase  = [0.0]*len(datfreq)

for i in range(len(datfreq)):
    datfreq[i] = float(datfreq[i])
    datreal[i] = float(datreal[i])
    datimag[i] = float(datimag[i])
    datmag[i] = np.abs(complex(datreal[i], datimag[i]))
    datphase[i] = np.angle(complex(datreal[i], datimag[i]))

selec_range = 2000
selec_range = len(datfreq)
selec_range = 4000
'''

def impedancelmfit(datfreq, datmag, datpointstart, datpointend, C0, L0, R10, R20, BNClen, numlumps, Cvary, Lvary, R1vary, R2vary, BNClenvary, numlumpsvary, path, dattimestring):

    datfreqselec = datfreq[datpointstart:datpointend]
    datmagselec = datmag[datpointstart:datpointend]
    
    #if (Cvary == 'False'): Cvary = False

    R1vary = str(R1vary)

    fit_params = Parameters()
    fit_params.add('C', value=C0, min =0, max=1, vary = bool(Cvary == 'True'))
    fit_params.add('L', value=L0, min=0, max=1, vary=bool(Lvary == 'True'))
    fit_params.add('R1', value=R10, min=0, max=1000, vary=bool(R1vary == 'True'))
    fit_params.add('R2', value=R20, min=0, max=1000, vary=bool(R2vary == 'True'))
    fit_params.add('BNClen', value=BNClen, vary=bool(BNClenvary == 'True'))
    fit_params.add('numlumps', value=numlumps, vary=bool(numlumpsvary == 'True'))
    #fit_params.add('R2', value=0, vary=False)

    out = lmfit.minimize(residual, fit_params, args=(datfreqselec,), kws={'data': datmagselec})

    #print(fit_report(out))
    
    vals = out.params.valuesdict()
    C = vals['C']
    L = vals['L']
    R1 = vals['R1']
    R2 = vals['R2']
    BNClen = vals['BNClen']
    numlumps = vals['numlumps']
    
    fitparamlist = [0.0]*len(datfreq)
    fitparamlist[0] = C
    fitparamlist[1] = L
    fitparamlist[2] = R1
    fitparamlist[3] = R2
    fitparamlist[4] = BNClen
    fitparamlist[5] = numlumps
    
    fitmodelmag, fitmodelphase = residual(out.params, datfreq)

    #Write to .csv file
    os.chdir(path)

    outfile = dattimestring+"fitparams.csv"
    if os.path.exists(outfile):
        os.remove(outfile)    
        
    formattedfile=open(outfile, 'a')

    formattedfile.write('C (F), L (H), R1 (Ohms), R2 (Ohms), BNClen (ft), numlumps \n')
    formattedfile.write(str(C)+','+str(L)+','+str(R1)+','+str(R2)+','+str(BNClen)+','+str(numlumps)+'\n')
    formattedfile.write('Allowed to vary in fit?')
    formattedfile.write('\n')
    formattedfile.write(Cvary+','+Lvary+','+R1vary+','+R2vary+','+BNClenvary+','+numlumpsvary+', \n')
    formattedfile.close()


    return([datfreq, fitmodelmag, fitmodelphase, fitparamlist])

'''
plt.grid(True)
plt.ylabel('Impedance (Ohms)')
plt.xlabel('frequency (Hz)')
plt.plot(datfreq, datmag, label=r'Data')
plt.plot(datfreq, residual(out.params, datfreq), label=r'fit')

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
'''
# <end of examples/doc_fitting_withreport.py>