from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import csv
import matplotlib.pyplot as plt
import numpy as np


#----------------------------------------------- README -----------------------------------------------------------
#       This software uses LinearDisciminantanalysis from the sklearn to execute a linear discriminant
#       analysis method to analyze and process emg signals from pre-recorded data. Specifically, this
#       method is intended for classification of muscle synergies into estimated one of six poses from
#       the open literature.
#------------------------------------------------------------------------------------------------------------------




#----------------------------------------------- PARAMETERS ------------------------------------------------------- 
# The LDA model parameters are defined here
LDA = LinearDiscriminantAnalysis()
#------------------------------------------------------------------------------------------------------------------




#----------------------------------------------- FUNCTION DEFINITIONS ---------------------------------------------
#       This section details the functions used in this program 

# FUNCTION:      readData 
# PURPOSE:       Reads a line of data from a csv file
# NEED:          Designed for use with open-source data

def readch1(rw,cols):
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

def readch2(rw,cols):
    emg_ = []
    with open('C:\\Users\\azb0180\\Downloads\\Github\\WeBR\\ASGC_2021\\code\\Test_data\\data\\cylindricalGraspChannel2.csv') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            k = (row[rw:cols])
        for i in range(0,len(k)):
            emg_.append(k[i])
            emg_[i] = float(emg_[i])
    emg_ = np.array(emg_)
    return emg_


# FUNCTION:      LDA_train
# PURPOSE:       Trains the LDA classifier
# NEED:          Needed to produce a trained LDA function for classification

def train(X,y):
    LDA.fit(X,y)
    LinearDiscriminantAnalysis()
    
# FUNCTION:      classify
# PURPOSE:       executes the trained classifier over input data, X
# NEED:          Needed to produce a hand pose classification

def classify(X):
    result = LDA.predict(X)
    return result
#------------------------------------------------------------------------------------------------------------------





#----------------------------------------------- FUNCTION CALLS ---------------------------------------------------

# DEFINE CONSTANTS:    define the # of signals and length of sliding window:
lenSigs = 2500
lenWindow = 10
f_s = 500
trial = 0

# IMPORT DATA:         Read signals to be iterated over   
chnl_1 = abs(readch1(trial,lenSigs))
chnl_2 = abs(readch2(trial,lenSigs))

# MAIN LOOP:           Perform a sliding window analysis over the length of the signals

# training data
X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
y = np.array([1, 1, 1, 2, 2, 2])


train(X,y)
x = [[-0.8, -1]]
print(classify(x))

#------------------------------------------------------------------------------------------------------------------
