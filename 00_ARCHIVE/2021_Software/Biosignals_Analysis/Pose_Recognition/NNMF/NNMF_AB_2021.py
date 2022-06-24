from numpy.core.fromnumeric import size
from sklearn.decomposition import NMF as nmf
import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy import signal

#----------------------------------------------- README -----------------------------------------------------------
#       This software uses NMF from the sklearn matrix decomposition package set to execute non-negative   
#       matrix factorization (nmf) analysis to process emg signals from pre-recorded data. The method   
#       used here follows "Fast local algorithms for large scale regarding nonnegative matrix and tensor 
#       factorizations" in accordance with the literature regarding Neural pattern analysis. The intent 
#       of this code is to detect Neuromuscular patterns during common hand grasps (selected from the 
#       literature).
#------------------------------------------------------------------------------------------------------------------




#----------------------------------------------- PARAMETERS ------------------------------------------------------- 
# The NMF model parameters are defined here
nRows = 2
nColumns = 1
nComponents = nRows*nColumns
nmfModel = nmf(nComponents,init='random')
#------------------------------------------------------------------------------------------------------------------




#----------------------------------------------- FUNCTION DEFINITIONS ---------------------------------------------
#       This section details the functions used in this program 

# FUNCTION:      readData 
# PURPOSE:       Reads a line of data from a csv file
# NEED:          Designed for use with open-source data

def readch1(rw,cols):
    emg_ = []
    with open('/home/avinash/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset2/01/01_2.csv') as csvfile:
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
    with open('/home/avinash/Github/WeBR/ASGC_2021/Software/SUPPORT/Test_data/EMG_dataset2/01/01_3.csv') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[rw:cols])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    emg_ = np.array(emg_)
    return emg_


# FUNCTION:      nmf_ 
# PURPOSE:       Uses the defined NMF model to decompose data
# NEED:          Needed to produce W, a matrix of synergies

def nmf_(X):
    W = nmfModel.fit_transform(X)
    H = nmfModel.components_
    return W,H

#------------------------------------------------------------------------------------------------------------------





#----------------------------------------------- FUNCTION CALLS ---------------------------------------------------

# DEFINE CONSTANTS:    define the # of signals and length of sliding window:
lenSigs = 20000
lenWindow = 10
f_s = 1000
trial = 0

# IMPORT DATA:         Read signals to be iterated over   
chnl_1 = abs(readch1(trial,lenSigs))
chnl_2 = abs(readch2(trial,lenSigs))

# MAIN LOOP:           Perform a sliding window analysis over the length of the signals
h_factor1 = []
h_factor2 = []
w_factor=[]
sig_plt = []
cNMF = []
synerg_norm = []
for i in range(lenSigs):    
    readings_ch1 = chnl_1[i]
    readings_ch2 = chnl_2[i]
    sig_plt.append(readings_ch1)
    data = np.array([[readings_ch1, readings_ch2]])
    [W, H] = nmf_(data)
    # print(W)
    # print('\n')
    h_factor1.append(0.1*np.mean(H[1,0]))
    h_factor2.append(0.1*np.mean(H[1,1]))
    w_factor.append(W[0,0])
    synerg_norm.append(H[1,0]*H[1,1])
#print(h_factor)
# print('\n')
    
# REPORT RESULTS:
#cNMF = np.convolve(h_factor1,h_factor2)
ps=0.01*(np.abs(np.fft.fft(h_factor1))**2)
time_step = 1 / 1000
#freqs = np.fft.fftfreq(h_factor1.size, time_step)
# idx = np.argsort(freqs)

cNMF = cNMF[0:lenSigs]
fig, ax = plt.subplots()
ax.set_title('Syngergy  Modeling via TFD')
ax.set_ylabel('Magnitude')
ax.set_xlabel('time (10 sec epochs)')
# function to plot and show graph
l1, = ax.plot(h_factor1, c='y', label ='Synergy A Excitation Energy',linewidth=0.30)
l3, = ax.plot(h_factor2, c='g', label ='Synergy B Excitation Energy',linewidth=0.30)
l2, = ax.plot(sig_plt, c='b', label='EMG Signal',linewidth=0.250)
#l4, = ax.plot(freqs[idx], ps[idx], c='m', label='EMG Signal',linewidth=0.50)
#l4, = ax.plot(freqs[idx], ps[idx], c='m', label='EMG Signal',linewidth=0.50)
ax.legend(handles=[l2, l3,l1])
plt.rc('font', size=30)
plt.rc('axes', titlesize=30)
#plt.plot(sig_plt)#, title="signal TFD Power")
plt.show()


#------------------------------------------------------------------------------------------------------------------
