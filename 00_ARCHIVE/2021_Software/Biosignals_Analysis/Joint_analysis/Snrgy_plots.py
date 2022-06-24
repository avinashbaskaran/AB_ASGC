from os import read
from numpy.core.fromnumeric import size, shape
from  scipy import signal
import scipy
from scipy.signal.spectral import periodogram
import scipy.signal as sig 
from scipy.fft import fft, ifft, fftfreq
import math
import numpy as np
import csv
import matplotlib.pyplot as plt
#from scipy.stats.morestats import Variance
import tftb
from collections import defaultdict
from scipy import integrate
from sklearn.decomposition import NMF as nmf
from scipy.stats import pearsonr
import statistics 
from scipy.optimize import curve_fit


#----------------------------------------------- README -----------------------------------------------------------
#       This software uses time-frequency (ie. Wigner-Ville Distribution) analysis to characterize   
#       and process emg signals from pre-recorded data. The method used here follows    
#       Cohen's class of time-frequency distribution, in accordance with the literature regarding 
#       fatigue analysis during non-isometric contractions. The intent of this code is to detect
#       fatigue during common hand grasps (selected from the literature).
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------FUNCTION DEFINITIONS-----------------------------------------------
#       This section details the functions used in this program 

def readch1(rw,cols):
    emg_ = []
    #with open('/home/avinash/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset1/DBs_raw/Database_2/male_day_1_cylindrical.csv') as csvfile:
    with open('C:/Users/azb0180/Downloads/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset1/DBs_raw/Database_2/male_day_1_cylindrical.csv') as csvfile:
   
        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[rw:cols])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    emg_ = np.array(emg_)
    return emg_

def readch2(rw,cols):
    emg_ = []
    #with open('/home/avinash/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset1/DBs_raw/Database_2/male_day_1_cylindrical.csv') as csvfile:
    with open('C:/Users/azb0180/Downloads/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset1/DBs_raw/Database_2/male_day_1_cylindrical.csv') as csvfile:
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

def tfd(ps,window):
    complex_product = 0
    for i in range(window):
        psreal=np.real(ps[i])
        psimagn=np.imag(ps[i])
        compl = psreal + psimagn
        compl_conj = psreal - psimagn
        complex_product=complex_product+compl*compl_conj
        # wvdistr = complex_product * math.e^(-1j)
    complex_product = complex_product*window
    return complex_product


# FUNCTION:      nmf_ 
# PURPOSE:       Uses the defined NMF model to decompose data
# NEED:          Needed to produce W, a matrix of synergies

def nmf_(X):
    W = nmfModel.fit_transform(X)
    H = nmfModel.components_
    return W,H

def norm(X):
    ar = X/np.max(X)
    return ar
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------

#----------------------------------------------- FUNCTION CALLS ---------------------------------------------------
# DEFINE CONSTANTS:    define the # of signals and length of sliding window:
# General and TFD
lenSigs = 12000
lenWindow = 10
dt = 1/500    
f_s = 500
trial = 0

# NNMF
nRows = 2
nColumns = 1
nComponents = nRows*nColumns
nmfModel = nmf(nComponents,init='random')

# IMPORT DATA:         Read signals to be iterated over   
# signals = readRow(trial,lenSigs)
chnl_1 = abs(readch1(trial,lenSigs))
chnl_2 = abs(readch2(trial,lenSigs))

# TFD data:
tfdplot=[]
MAV_ = []
MF_ = []
TFR_ = []
readings_plt = []
data_tf=[]
# NNMF data:
h_factor1 = []
h_factor2 = []
w_factor=[]
sig_plt = []
cNMF = []
synerg_norm = []

emgplt = []
ftg_sng = []
# # MAIN LOOP:           Perform a sliding window analysis over the length of the signals
for i in range(1, int(lenSigs/lenWindow),1):
    readings_ch1 = chnl_1[(i)*10:(i+1)*10]
    readings_ch2 = chnl_2[(i)*10:(i+1)*10]
    a = np.nanmean(readings_ch1)
    b = np.nanmean(readings_ch2)
    data_tf = readings_ch1
    data_mf = np.array([[a, b]])
    #   NNMF:   
    [W, H] = nmf_(data_mf)
    h_factor1.append(np.mean(H[1,0]))
    h_factor2.append(np.mean(H[1,1]))
    w_factor.append(W[0,0])
    
    #   TFD:
    freqs, power = periodogram(data_tf, fs=1000)
    MAV = integrate.cumtrapz(data_tf)/dt                                      # A) Mean Average Voltage
    area_freq = integrate.cumtrapz(power, freqs, initial=0)                    
    total_power = area_freq[-1]
    MFadd = [freqs[np.where(area_freq >= total_power / 2)[0][0]]]              # B) Median Frequency
    tfr = tftb.processing.WignerVilleDistribution(data_tf)                    
    tfr_wvd,t_wvd,f_wvd = tfr.run()                                            # D) TFD 
    sig_plt.append(readings_ch1)
    TFR_.append(np.mean(tfr_wvd[1]))
    MAV_.append(np.mean(MAV))
    MF_.append(MFadd[0])
    ftg_sng.append(statistics.pvariance(tfr_wvd[1]))#*np.mean(H[1,0]))
    #print(statistics.pvariance(tfr_wvd))
    ftg_sng.append(np.mean(tfr_wvd)*np.mean(H[1,0]))
    #ftg_sng.append(pearsonr(x, y))
cNMF = cNMF[0:lenSigs]

fig, axs = plt.subplots(4)
axs[2].set_ylabel('Normalized Magnitude')
axs[3].set_xlabel('time (10 ms epochs)')

# NORMALIZE
TFR_ = norm(TFR_)
MAV_ = norm(MAV_)
h_factor1 = norm(h_factor1)
h_factor2 = norm(h_factor2)
chnl_1 = norm(chnl_1)
ftg_sng = norm(ftg_sng)

l1, = axs[0].plot(chnl_2, c='b', label='EMG Signal',linewidth=1.0)
axs[0].legend(handles=[l1],loc='upper right')
axs[0].axes.xaxis.set_visible(False)
#axs[0].axes.yaxis.set_visible(False)
l2, = axs[1].plot(TFR_, c='r', label ='IMF',linewidth=1.0)
axs[1].legend(handles=[l2],loc='upper right')
axs[1].axes.xaxis.set_visible(False)
#axs[1].axes.yaxis.set_visible(False)
l3, = axs[2].plot(h_factor1, c='y', label ='EP A',linewidth=1.0)
axs[2].legend(handles=[l3],loc='upper right')
axs[2].axes.xaxis.set_visible(False)
#axs[2].axes.yaxis.set_visible(False)
l4, = axs[3].plot(h_factor2, c='g', label ='EP B',linewidth=1.0)
axs[3].legend(handles=[l4],loc='upper right')
#axs[3].axes.yaxis.set_visible(False)

plt.rc('font', size=20)
plt.rc('axes', titlesize=30)
plt.show()