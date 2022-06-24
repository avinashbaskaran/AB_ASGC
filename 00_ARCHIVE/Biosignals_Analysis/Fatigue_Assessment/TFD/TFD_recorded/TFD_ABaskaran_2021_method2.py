import tftb
from scipy import integrate
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
nperseg = lenSigs*1/f_s
# IMPORT DATA:         Read signals to be iterated over   
signals = readData(trial,lenSigs)
tfr_wvd_question = []
# MAIN LOOP:           Perform a sliding window analysis over the length of the signals
for i in range(1, int(lenSigs/lenWindow),1):    
    readings = signals[(i-1)*10:i*10]
    f_stft, t_stft, Zxx = signal.stft(readings, f_s, nperseg=nperseg, noverlap=nperseg-1, return_onesided=False)

    # shifting the frequency axis for better representation
    Zxx = np.fft.fftshift(Zxx, axes=0)
    f_stft = np.fft.fftshift(f_stft)

    # Doing the WVT
    wvd = tftb.processing.WignerVilleDistribution(readings, timestamps=np.arange(10)*(1/f_s))
    tfr_wvd, t_wvd, f_wvd = wvd.run()
    for i in range(0,10):
        tfr_wvd_question.append(tfr_wvd[0,i])
    #print(tfr_wvd[0])
tfr_wvd_FFT = fft(tfr_wvd_question)
tfr_wvd_FFT_intgr = integrate.cumtrapz(tfr_wvd_FFT)
tfdplot= ifft(tfr_wvd_FFT_intgr)
tfdplot[0] = 0
# for i in range(0,len(tfdplot)):
#     tfdplot[i] = math.sqrt(abs(tfdplot[i]))
# print(len(j))
# np.concatenate([tfdplot,j])
# REPORT RESULTS:
#plt.plot(adjamplplot)#, title="signal TFD Power")

print(tfdplot)
plt.plot(tfdplot) #, title="signal TFD Power")
# plt.plot(signals) #, title="signal TFD Power")

plt.show()

#------------------------------------------------------------------------------------------------------------------
