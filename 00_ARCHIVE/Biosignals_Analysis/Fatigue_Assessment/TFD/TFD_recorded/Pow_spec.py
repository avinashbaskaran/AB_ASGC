import time
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import math
###################################################################################################
####################################    FUNCTIONS   ###############################################
###################################################################################################
## A series of functions for reading and analyzing EMG signals:
## Read data from csv (j data points from a single row)
def read6(j):
    emg_ = []
    with open('C:\\Users\\azb0180\\Downloads\\Github\\WeBR\\ASGC_2021\\DB2_DAY1_MALE1_C1.csv') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[0:j])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    return emg_

def iemg(emg,lEpoch):
    i = int(math.floor(len(emg)/lEpoch))
    iemg_=[]
    iemgx_=[]
    for j in range(0,i):
        l = 0
        for k in range(0,lEpoch-1):
            intgrl = abs(emg[j*lEpoch+k])/lEpoch
            l = l+intgrl
        iemgx_.append(j*lEpoch)
        iemg_.append(l)
    return iemgx_,iemg_

def max_iemg(iemg,lEpoch,lEpoch2):
    maxiemgx_=[]
    maxiemg_=[]
    i = int(math.floor(len(iemg)/lEpoch2))
    for j in range(0,i):
        prevmax_=0
        max_=0
        for k in range(0,lEpoch2-1):
            max_ = max(iemg[j*lEpoch2+k],prevmax_)
            prevmax_=max_     
        maxiemgx_.append(lEpoch*(j*lEpoch2))
        maxiemg_.append(max_)
    return maxiemgx_,maxiemg_
    
def rmsemg(emg,lEpoch2):
    i = int(math.floor(len(emg)/lEpoch2))
    rmsemgx_=[]
    rmsemg_=[]
    for j in range(0,i):
        l = 0
        for k in range(0,lEpoch-1):
            rms = ((emg[j*lEpoch+k])^2)
            l = l+rms
        rms = math.sqrt(l/(lEpoch2-1))
        rmsemgx_.append(j*lEpoch)
        rmsemg_.append(rms)
    return rmsemgx_,rmsemg_
###################################################################################################
####################################    RUN PARAMETERS   ##########################################
###################################################################################################
## A 6th order autoregressive (AR) model describing Neuromuscular Effort
## (EMG smoothing / future estimation)
n = 1
modl_ordr = 6                       # The model order (6th order)
##  A measure of integrated EMG 
## (NME calculation)
lEpoch = 3
## A measure of max integrated EMG 
## (NME calculation)
lEpoch2 = 5
## A measure of rms EMG 
## (NME calculation)
lEpoch3 = 5

##################################################################################################
####################################    FUNCTION CALLS   #########################################
##################################################################################################
emg_ = read6(2000)
iemgx_,iemg_ = iemg(emg_,lEpoch)
maxiemgx_,maxiemg_=max_iemg(iemg_,lEpoch,lEpoch2)
rmsemgx_,rmsemg_=max_iemg(iemg_,lEpoch,lEpoch2)
plt.plot(emg_, 'g',label = 'emg',linewidth=1/2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        bbbbbbbbbbbb    
plt.plot(iemgx_,iemg_, 'r', label='iemg',linewidth=1/2)
plt.plot(maxiemgx_,maxiemg_, 'b',label = 'max emg',linewidth=1/2)
plt.plot(rmsemgx_,rmsemg_, 'y',label = 'rms emg',linewidth=1/2)
#print()
plt.ylabel('Myographic activity')
plt.legend()
plt.show()
