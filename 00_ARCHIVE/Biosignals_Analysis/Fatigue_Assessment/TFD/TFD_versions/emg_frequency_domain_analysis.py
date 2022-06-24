from __future__ import division
from numpy.lib.function_base import median
from numpy import linspace, where
from scipy import signal
from scipy.integrate import cumtrapz 
import csv
import numpy as np
import matplotlib.pyplot as plt
import math
###################################################################################################
####################################    FUNCTIONS   ###############################################
###################################################################################################
## A series of functions for reading and analyzing EMG signals:
## Read data from csv (j data points from a single row)
def readData(j):
    emg_ = []
    with open('C:\\Users\\azb0180\\Downloads\\Github\\WeBR\\ASGC_2021\\DB2_DAY1_MALE1_C1.csv') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[0:j])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    emg_ = np.array(emg_)
    return emg_

def pwrSpctrm(emgdata, sampling_rate):
    fourier_transf = np.abs(np.fft.rfft(emgdata))
    abs_fourier_transf = np.abs(fourier_transf)
    ps = np.square(abs_fourier_transf)
    freq = np.linspace(0,sampling_rate/2,len(ps))
    return freq, ps

def medFreq(freqs, pw,init,l_medFreq_Epoch):
    median_freq=[]
    i = int(math.floor(len(pw)/l_medFreq_Epoch))
    rmsemgx_=[]
    rmsemg_=[]
    for j in range(0,i):
        l = 0
        for k in range(0,l_medFreq_Epoch-1):
            rms = ((pw[j*l_medFreq_Epoch+k])^2)
            l = l+rms
        rms = math.sqrt(l/(l_medFreq_Epoch-1))
        rmsemgx_.append(j*l_medFreq_Epoch)
        rmsemg_.append(rms)
    total_power = area_freq[-1]
    median_freq += freqs[where(area_freq>=total_power/2)[0][0]]
    return median_freq, ps


###################################################################################################
####################################    RUN PARAMETERS   ##########################################
###################################################################################################
##  A measure of integrated EMG 
## (NME calculation)
l_medFreq_Epoch = 5
##################################################################################################
####################################    FUNCTION CALLS   #########################################
##################################################################################################
emg_ = readData(2500)
frequencies,ps = pwrSpctrm(emg_,0.1)
med_freqs = medFreq(frequencies,ps,0,l_medFreq_Epoch)
#plt.plot(emg_, 'g',label = 'emg',linewidth=1/2)    
plt.semilogy(frequencies,ps, 'g',label = 'emg power spectrum',linewidth=1/2) 
plt.ylabel('intensity')
plt.legend()
plt.show()
