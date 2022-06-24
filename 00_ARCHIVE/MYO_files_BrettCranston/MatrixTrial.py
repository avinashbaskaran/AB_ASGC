# from scipy.io import loadmat
# 
# matrix = loadmat('/home/pi/Desktop/OddsMatrix.mat')
import os
import busio
import numpy as np
import scipy.io as sp
import math as m


matrix = sp.loadmat('/home/pi/Desktop/OddsMatrix.mat')

x = np.array(matrix['finalMatrix'])
f = np.array([2,4,6,8,10,12,14,16])
oddsArray = np.zeros((8,8))
oddsArray2 = np.zeros((8,8))
row = 0
col = 1
value = 0
odd = 1
while(row <= 6):
    col = row +1
    while(col <= 7):
        
        index = m.floor((f[row] / f[col])*2)
        odd = x[1,row,col,index] * odd
        print(odd)
        
        col = col+1
    row = row+1


