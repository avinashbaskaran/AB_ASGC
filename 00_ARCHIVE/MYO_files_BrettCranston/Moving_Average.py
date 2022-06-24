
import logging
import binascii     #Byte array to Hex
import time
import struct
import math
import numpy as np

try:
    
    a = np.array([1,2,3,4,5,6,7,8])
    b = np.array([9,10,11,12,13,14,15,16])
    c = np.array([9,10,11,12,13,14,15,16])
    d = np.array([9,10,11,12,13,14,15,16])
    e = np.array([9,10,11,12,13,14,15,16])
    f = np.row_stack((a,b,c,d,e))
    h = np.zeros((10,8))

    g = np.mean(f,axis=0)
    x = 0/5
    h[3] = c
    print(g[0])
    print(h)
    print(g)
finally:
    np.savetxt("./PoseData/foo.csv", f, fmt = '%d', delimiter=" ")



