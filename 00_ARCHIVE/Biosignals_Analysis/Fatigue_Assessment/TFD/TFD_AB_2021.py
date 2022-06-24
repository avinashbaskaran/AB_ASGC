from numpy.core.fromnumeric import shape
from  scipy import signal
import scipy
from scipy.signal.spectral import periodogram
import scipy.signal as sig 
from scipy.fft import fft, ifft, fftfreq
import math
import numpy as np
import csv
import matplotlib.pyplot as plt
import tftb
from collections import defaultdict
from scipy import integrate




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


# FUNCTION:      readData 
# PURPOSE:       Reads data from a csv file
# NEED:          Designed for use with open-source data

def readRow(rw,cols):
    emg_ = []
    # with open('C:\\Users\\azb0180\\Downloads\\Github\\WeBR\\ASGC_2021\\Software\\Support\\Test_data\\EMG_dataset2\\01\\01_2.csv') as csvfile:
    with open('C:/Users/azb0180/Downloads/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset1/DBs_raw/Database_2/male_day_1_cylindrical.csv') as csvfile:

        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[rw:cols])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    emg_ = np.array(emg_)
    return emg_

def readCol(rws,col):
    emg_ = defaultdict(list)
    # with open('C:\\Users\\azb0180\\Downloads\\Github\\WeBR\\ASGC_2021\\code\\SUPPORT\\Test_data\\EMG_dataset2\\01\\01_2.csv') as csvfile:
    with open('C:/Users/azb0180/Downloads/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset1/DBs_raw/Database_2/male_day_1_cylindrical.csv') as csvfile:

        reader = csv.DictReader(csvfile) # read rows into a dictionary format
        emg_=list(reader) 
    emg_ = np.array
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
lenSigs = 10000
lenWindow = 10
f_s = 1
trial = 0
tfdplot=[]

# IMPORT DATA:         Read signals to be iterated over   
signals = readRow(trial,lenSigs)
MAV_ = []
MF_ = []
TFR_ = []
readings_plt = []

# # MAIN LOOP:           Perform a sliding window analysis over the length of the signals
for i in range(1, int(lenSigs/lenWindow),1):
    dt = 10    
    readings = signals[(i-1)*10:i*10]
    freqs, power = periodogram(readings, fs=1000)
    MAV = integrate.cumtrapz(readings)/dt                                      # A) Mean Average Voltage
    area_freq = integrate.cumtrapz(power, freqs, initial=0)                    
    total_power = area_freq[-1]
    MFadd = [freqs[np.where(area_freq >= total_power / 2)[0][0]]]              # B) Median Frequency
    tfr = tftb.processing.WignerVilleDistribution(readings)                    
    tfr_wvd,t_wvd,f_wvd = tfr.run()                                            # D) TFD 
 
    TFR_.append(100*np.mean(tfr_wvd))
    MAV_.append(np.mean(MAV))
    MF_.append(0.000001*MFadd[0])

#   readings_plt.append(np.mean(readings))

fig, ax = plt.subplots()
ax.set_title('Fatigue Modeling via TFD')
ax.set_ylabel('Magnitude')
ax.set_xlabel('time (10 sec epochs)')
# function to plot and show graph
l1, = ax.plot(TFR_, c='r', label ='Instantaneous Mean Frequency, per TFD',linewidth=0.60)
l2, = ax.plot(MAV_, c='b', label='Mean Average Voltage',linewidth=0.250)
ax.legend(handles=[l2, l1])
plt.rc('font', size=30)
plt.rc('axes', titlesize=30)
plt.show()
# REPORT RESULTS:

#plt.plot(MF_)
#plt.plot(readings_plt)
# REPORT RESULTS:


#------------------------------------------------------------------------------------------------------------------