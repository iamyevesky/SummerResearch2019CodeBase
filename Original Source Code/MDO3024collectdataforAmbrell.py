import os, sys, time
import matplotlib.pyplot as plt
import visa
import numpy
from time import gmtime, strftime
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

visa_address = 'TCPIP::169.254.3.117::INSTR'
#visa_address = 'USB::0x0699::0x0408::C043120::INSTR'

opsens_visa_address = 'ASRL3::INSTR'

def set_default(scope):
    #scope.write(":WFMOutpre:BYT_Nr 1")
    #scope.write(":WFMInpre:NR_Pt 10000")
    #scope.write(":DATA:ENCDG ASCII")
    #scope.write(":DATA:STOP 10000")
    scope.write(":SELECT:CH1 on")
    #scope.write(":SELECT:CH2 on")
    scope.write(":SELECT:CH3 on")
    #scope.write(":DATa:SOUrce CH1")

    scope.write(":DATA:ENCDG ASCII")
    #scope.write(":DATA:ENCDG RIB")
    #scope.write(":WFMOutpre:ENCDG BIN")
    #scope.write(":WFMOutpre:BN_Fmt RI")
    #scope.write(":WFMOutpre:BYT_Nr 2")
    #scope.write(":WFMOutpre:BIT_Nr 16")
    #scope.write(":WFMInpre:YMULT 1.0e-3")
    #scope.write(":DATA:STOP 1000")
    #scope.write(":DATa:SOUrce CH1")
    #scope.write(":HORIZONTAL:RECORDLENGTH 1000")

def convert_raw_voltage_data(raw_data, scope):
    ymult = float(scope.query('WFMOutpre:YMULT?'))
    yzero = float(scope.query('WFMOutpre:YZERO?'))
    yoff = float(scope.query('WFMOutpre:YOFF?'))
    print('ymult= '+str(ymult))
    print('yzero= '+str(yzero))
    print('yoff= '+str(yoff))
    npoint=len(raw_data)
    voltage=['?']*npoint
    for i in range(npoint):
        voltage[i]=ymult*(raw_data[i]-yoff)+yzero
    return voltage

def set_channel(scope, channel):
    #scope.write('*WAI')
    scope.write(":DATa:SOUrce CH"+str(channel))
    #time.sleep(20)  

def get_data(scope):
    #scope.write('*OPC')
    #scope.write('*WAI')
    #time.sleep(5)
    scope.write("WFMOutpre:ENCdg ASCii")
    data = scope.query_ascii_values("CURVE?")
    #scope.write('*OPC')
    #scope.write('*WAI')
    #time.sleep(5)
    #print(data)
    #raw_data, status=scope.read(scope.session, scope.bytes_in_buffer)
    voltage=convert_raw_voltage_data(data, scope)
    return voltage

def print_data_Nch(scope, times, dt, voltage, outfile, numchan, stime, timeins):
    #nv1=len(voltage1)
    #nv2=len(voltage2)
    #if (nv1<nv2):
    #    size=nv1
    #else:
    #    size=nv2
    #os.system('DEL '+outfile)
    file=open(outfile, 'a')
    file2 = open(outfile+'.header', 'a')
    #freq = scope.query('AFG:frequency?')
    #file2.write('AFG frequency = '+str(freq)+' Hz')
    file2.write('Sample Interval,'+str(dt)+',\n')
    for j in range(numchan):
        term = scope.query('CH'+str(j+1)+':termination?')
        file2.write('CH'+str(j+1)+' termination:'+str(term))
    file2.write('Time: '+str(stime)+'\n')
    file2.write('Time in seconds since epoch: '+str(timeins)+'\n')
    file.write('TIME')
    for j in range(numchan):
        file.write(', CH'+str(j+1))
    file.write('\n')
    for i in range(len(voltage[0])):
        file.write(str(times[i]))
        for j in range(numchan):
            file.write(','+str(voltage[j][i]))
        file.write('\n')
#    opsfile.write(str(timeins)+','+str(op1)+','+str(op2)+'\n')

def get_time(scope, record_length):
    times=['?']*record_length
    xincr = float(scope.query('WFMOutpre:XINCR?'))
    print('xincr= '+str(xincr))
    for i in range(record_length):
        times[i]=float(i)*xincr
    return times  

def get_dt(scope):
    #scope.write('*WAI')
    xincr = float(scope.query('WFMOutpre:XINCR?'))
    return xincr


def calc_wait_time(scope):
    record_length=float(scope.query(':HORIZONTAL:RECORDLENGTH?'))
    dt=get_dt(scope)
    wait_time=record_length*dt
    return wait_time

def checkscale(scope, numchan, short_record_length, long_record_length):
    base_record_length=int(scope.query(':HORIZONTAL:RECORDLENGTH?'))
    time.sleep(calc_wait_time(scope))
    if short_record_length != base_record_length:
        scope.write(':Horizontal:Recordlength '+str(short_record_length))
        time.sleep(calc_wait_time(scope))
    hscale = 0.000000001*short_record_length*0.1
    scope.write(":Horizontal:Scale "+str(hscale))
    time.sleep(calc_wait_time(scope))
    scope.write('DATA:START 1')
    time.sleep(calc_wait_time(scope))
    scope.write('DATA:STOP '+str(short_record_length))
    time.sleep(calc_wait_time(scope))
    scope.write('ACQUIRE:STOPAFTER RUnsTOP')
    time.sleep(calc_wait_time(scope))
    for i in range(numchan):
        okayscale = 0
        while okayscale == 0:
            set_channel(scope, i+1)
            scope.write("WFMOutpre:ENCdg ASCii")
            time.sleep(calc_wait_time(scope))
            data = scope.query_ascii_values("CURVE?")
            highcount = 0
            lowcount = 0
            for j in range(short_record_length):
                if data[j] > 32760:
                    highcount += 1
                elif data[j] < 32760/5:
                    lowcount += 1
            if highcount/short_record_length > 0.0001:
                chscale = float(scope.query("CH"+str(i+1)+":SCALE?"))
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

def read_and_write_data_from_Nch(scope, outfile, figfilelist, nstart, descriptor, short_record_length, long_record_length):
    numchan = len(figfilelist)
    #opsens.write("CHannel1:DATA? 1")
    #checkscale(scope, numchan, short_record_length, long_record_length)
    time.sleep(0.01)    
    wait_time = calc_wait_time(scope)
    record_length=int(scope.query(':HORIZONTAL:RECORDLENGTH?'))
    scope.write('DATA:START 1')
    scope.write('DATA:STOP '+str(record_length))
    scope.write('acquire:stopafter sequence')
    stime=strftime("%c")
    timeins = time.time()
    voltage = [['?']*(record_length)]*numchan
    for i in range(numchan):
        set_channel(scope, i+1)
        time.sleep(0.01)
        voltage[i]=get_data(scope)                
        time.sleep(wait_time)
    #try:
    #    op1 = opsens.read_ascii_values(converter='s')
    #except:
    #    print('ERROR!!')
    #    op1 = 'Error'
    #try:
    #    op2 = opsens.read_ascii_values(converter='s')   
    #except:
    #    print('ERROR!!')
    #    op2 = 'Error'
    #opsens.clear()
    set_channel(scope, 1)
    #voltage2=get_data(scope)
    time.sleep(0.01)
    times=get_time(scope, record_length)
    time.sleep(0.01)
    dt=get_dt(scope)
    time.sleep(0.01)
    print_data_Nch(scope, times, dt, voltage, outfile, numchan, stime, timeins)
    scope.write('FPAnel:PRESS runstop')
    for i in range(numchan):
        plot_the_data(scope, nstart, i, times, voltage[i], figfilelist[i], descriptor)

def plot_the_data(scope, nstart, i, times, voltage, figoutfile, descriptor):
    plt.tight_layout()
    colorlist = ['w-', 'y-', 'c-', 'm-', 'g-']
    plt.style.use('dark_background')
    plt.figure(nstart+i) 
    plt.plot(times, voltage, colorlist[i+1])
    plt.title('Voltage Channel '+str(i+1)+' '+descriptor)
    plt.grid(True)
    plt.xticks(rotation=90)
    plt.xlabel('Time (s))')
    plt.ylabel('Voltage (V)')
    plt.savefig(figoutfile)
    plt.show()
    plt.close()
    #print('Plot acquired')


def mainforAmbrell(numchan, timesubf, nstart, descriptor, j, short_record_length, long_record_length):
    ###################Modify these parameters########################
    basedir=r'''C:\Research\data\TektronixMDO3024'''
    datesubf = strftime("%Y%m%d")
    filename = descriptor+'-'+str(j)
    #opsfilename = descriptor
    outdir = basedir+'\\'''+datesubf+'\\'''+timesubf
    outfile = outdir+'\\'''+filename+'.txt'
    #opsoutfile = outdir+'\\'+opsfilename+'temps.txt'
    figfilelist = ['?']*numchan
    for i in range(numchan):
        figfilelist[i] = outdir +'\\'''+filename+'voltage'+str(i+1)+'.pdf'
    ##################################################################

    print('Starting')
    if not os.path.exists(outdir):
        print('Creating directory')
        os.makedirs(outdir)
    #opsfile = open(opsoutfile, 'a')
    #opsfile.write('Time since epoch, T1, T2 \n')
    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
#    opsens = rm.open_resource(opsens_visa_address, baud_rate = 9600, data_bits = 8, write_termination= '\r', read_termination = '\4')
    print(scope.query("*IDN?"))
    #time.sleep(0.01)
    #wait_time = calc_wait_time(scope)
    time.sleep(0.01)
#    scope.write(':Horizontal:Recordlength 10000')
#    time.sleep(calc_wait_time(scope))
    scope.write('Data:width 2')
    time.sleep(0.01)
    #scope.close()
    #scope = rm.open_resource(visa_address)    
    #print('writing *RST to scope')
    #scope.write('*RST')
    #print('writing *CLS to scope')
    #scope.write('*CLS')
    #print('setting scope query_delay to 20 seconds (original was 1000!)')
    #scope.query_delay=20.0
    #print(scope.query("*IDN?"))
    #outfile=out_dir+'\test.txt'
    #set_default(scope)
    read_and_write_data_from_Nch(scope, outfile, figfilelist, nstart, descriptor, short_record_length, long_record_length)
    errors=scope.query('ALLEV?')
    print('errors= '+str(errors))
    errors=scope.query('*ESR?')
    print('errors= '+str(errors))
    scope.close()
#    opsens.close()
    return(nstart+numchan, outdir)


#numchan = 3
#main(numchan, test, 0, 300000)


