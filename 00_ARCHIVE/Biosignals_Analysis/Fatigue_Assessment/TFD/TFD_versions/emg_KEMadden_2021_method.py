from  scipy import signal
import math
####### Filtering ######
########################
# Raw sEMG signals bandpass filtered from 10 to 400 hz
# using a 4th order Butterworth filter (zero-lag, non-causal)

def BP_filter_design(fs, order, lowcut, highcut):
    nyq = fs/2
    low = lowcut/nyq
    high = highcut/nyq
    b,a= signal.butter(order,low,high,'bandpass',analog=True) # (order, critical frequencies,btype,analog v. digital)
    return b,a

def data_filter(data,lowcut,highcut,fs, order):
    b,a = BP_filter_design(fs, order,lowcut,highcut)
    filtered_data = signal.lfilter(b,a,data)
    return filtered_data

####### Feature Exctraction #######
###################################
# Need to capture how the signal energy changes
# in both the time and frequency domains.

# Will use Cohen's class of time-frequency distributions (TFD)
# to obtain a two-dimensional probability density function, C(t,w)
# to describe the joint distribution of energy of the sEMG signal,
# s(t), over time, t, and frequency, w

def emg_ftrs(singal):
    C(t,w) = 1/(4*math.pi^2) *  
