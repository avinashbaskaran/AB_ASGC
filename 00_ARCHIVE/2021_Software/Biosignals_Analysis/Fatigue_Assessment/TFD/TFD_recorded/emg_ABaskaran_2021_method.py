from  scipy import signal
from scipy.fft import fft, ifft, fftfreq
import math
import numpy as np
import csv
import matplotlib.pyplot as plt
#----------------------------------------------- README -----------------------------------------------------------
#       This software executes bilinear time-frequency distribution (tfd) analysis (ie. Wigner-Ville   
#       Distribution) to process emg signals from pre-recorded data. The method used here follows    
#       Cohen's class of time-frequency distribution, in accordance with the literature regarding 
#       fatigue analysis during non-isometric contractions. The intent of this code is to detect
#       fatigue during common hand grasps (selected from the literature).
#------------------------------------------------------------------------------------------------------------------






#-----------------------------------------------FUNCTION DEFINITIONS-----------------------------------------------
#       This section details the functions used in this program 


# FUNCTION:      readData 
# PURPOSE:       Reads data from a csv file
# NEED:          Designed for use with open-source data

def readData(rw,cols):
    emg_ = []
    with open('C:\\Users\\azb0180\\Downloads\\Github\\WeBR\\ASGC_2021\\code\\Test_data\\data\\cylindricalGraspChannel1.csv') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[rw:cols])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    emg_ = np.array(emg_)
    return emg_


# FUNCTION:      BP_filter_design 
# PURPOSE:       Design of a bandpass filter for 10 to 400 hz (4th order Butterworth filter (zero-lag, non-causal))
# MOTIVATION:    Designed to conform process to literature

def BP_filter_design(fs, order, lowcut, highcut):
    nyq = fs/2
    low = lowcut/nyq
    high = highcut/nyq
    b,a= signal.butter(order,low,high,'bandpass',analog=True) 
        #signal.butter(order, critical frequencies,btype,analog v. digital)
    return b,a


# FUNCTION:      data_filter
# PURPOSE:       Implementation of the designed filter
# MOTIVATION:    Executes the designed filter over selected data 

def data_filter(data,lowcut,highcut,fs, order):
    b,a = BP_filter_design(fs, order,lowcut,highcut)
    filtered_data = signal.lfilter(b,a,data)
    return filtered_data
    # real and complex portions saved for later

# FUNCTION:     pwrSpctrm
# PURPOSE:      Use fast fourier transfrom (fft) to find power spectrum of data (in frequency domain)
# MOTIVATION:   Needed for tfd equation

def pwrSpctrm(emgdata,f_s):#, sampling_rate):
    fourier_complex = fft(emgdata)
    freqs = fftfreq(len(fourier_complex))*f_s
    return fourier_complex, freqs#, freq, ps


# FUNCTION:     tfd
# PURPOSE:      Extracts time-frequency domain features (changes in EMG signal energy)
# MOTIVATION:   Produces a term necessary for the tfd analysis in this code

def tfd0(ps,window):
    complex_product = 0
    for i in range(window):
        psreal=np.real(ps[i])
        psimagn=np.imag(ps[i])
        compl = psreal + psimagn
        compl_conj = psreal - psimagn
        complex_product=complex_product+compl*compl_conj
    complex_product = complex_product*window
    return complex_product
    
def tfd1(ps,window,f_s,tf):
    complex_product = 0
    for i in range(window):
        psreal=np.real(ps[i])
        psimagn=np.imag(ps[i])
        compl = psreal + psimagn
        compl_conj = psreal - psimagn
        complex_product=complex_product+(compl*compl_conj)*f_s/tf
    complex_product = complex_product*window
    return complex_product

#------------------------------------------------------------------------------------------------------------------



#----------------------------------------------- FUNCTION CALLS ---------------------------------------------------

# DEFINE CONSTANTS:    define the # of signals and length of sliding window:
lenSigs = 2500
lenWindow = 10
f_s = 500
trial = 0
tfdplot=[]
adjamplplot = [0]
freqintermedplot = [0]
# IMPORT DATA:         Read signals to be iterated over   
signals = readData(trial,lenSigs)

# MAIN LOOP:           Perform a sliding window analysis over the length of the signals
for i in range(1, int(lenSigs/lenWindow),1):    
    readings = signals[(i-1)*10:i*10]
    ps,freqs = pwrSpctrm(readings,f_s)
    tfd0_ = tfd0(ps,10)
    tfd1_ = tfd1(ps,10,f_s,tfd0_)
    adjamplplot.append(math.sqrt(abs(tfd0_)))
    freqintermedplot.append(tfd1_)
    print(tfd0_)
    tfdplot.append(tfd0_)    
    # print('\n')

# REPORT RESULTS:
#plt.plot(adjamplplot)#, title="signal TFD Power")
plt.plot(freqintermedplot)#, title="signal TFD Power")

plt.show()

#------------------------------------------------------------------------------------------------------------------
