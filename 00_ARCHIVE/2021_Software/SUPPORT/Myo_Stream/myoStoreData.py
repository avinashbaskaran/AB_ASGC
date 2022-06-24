import board
#import busio
import pygatt
import logging
import binascii     #Byte array to Hex
import time
import struct
import math
import numpy as np
import scipy.io as sp
import serial

EMG_Count = 0
#arduino = serial.Serial(port='/dev/ttyACM2', baudrate=115200, timeout=.1)


##################################################
# Insantiate Myo and Define UUID Characteristics #
##################################################

MAC = "F0:3E:E5:F2:F1:CD"
uuid_vendor = "d5060101-a904-deb9-4748-2c7f4a124842"
uuid_battery = "00002a19-0000-1000-8000-00805f9b34fb"   #Battery
command = "d5060401-a904-deb9-4748-2c7f4a124842"
uuid1 = "d506"
uuid2 = "-a904-deb9-4748-2c7f4a124842"
emgService = uuid1 + "0005" + uuid2
IMUService = uuid1 + "0002" + uuid2
emgChar0 = uuid1 + "0105" + uuid2
emgChar1 = uuid1 + "0205" + uuid2
emgChar2 = uuid1 + "0305" + uuid2
emgChar3 = uuid1 + "0405" + uuid2
IMUChar = uuid1 + "0402" + uuid2
pose = uuid1 + "0103" + uuid2

adapter = pygatt.GATTToolBackend()
#logging.basicConfig()
#logging.getLogger('pygatt').setLevel(logging.DEBUG)
adapter.start()
myo = adapter.connect(MAC)
 
#############################################
##### Inizializing Arrays for later use #####
#############################################
Accelerometer = [0, 0, 0]
Gyroscope = [0, 0, 0]
conversion = 180 / math.pi
emg_1 = [0,0,0,0,0,0,0,0]
emg_2 = [0,0,0,0,0,0,0,0]

#############################################
def Begin():
    global Posed
    global Angles    
    
def getBattery():
    battery = myo.char_read(uuid_battery)
    batteryOutput = int(binascii.hexlify(battery),16)
    print(batteryOutput)

def toEuler(w, x, y, z):
    sr_cp = 2 * (w*x + y*z)
    cr_cp = 1 - 2*(x*x + y*y)
    r = int(math.atan2(sr_cp, cr_cp) * conversion) + 180  # -180-180 -> 0-360
    
    sp = 2*(w*y - z*x)
    if abs(sp) >=1:
        p = int(math.copysign(math.pi / 2, sp) * conversion)
    else:
        p = int(math.asin(sp) * conversion) + 90          # -90-90 -> 0-180
        
    sy_cp = 2*(w*z + x*y)
    cy_cp = 1 - 2*(y*y + z*z)
    y = int(math.atan2(sy_cp, cy_cp) * conversion) + 180  # -180-180 ->   0-360
    
    
    return (r, p, y)

#############################################

def callback_IMU(handle,value):    
    global firstRun
    global rollSync
    raw_data = struct.unpack('<2s2s2s2s2s2s2s2s2s2s',value)
    
    w = int.from_bytes(raw_data[0], "little", signed = True) / 16384
    x = int.from_bytes(raw_data[1], "little", signed = True) / 16384
    y = int.from_bytes(raw_data[2], "little", signed = True) / 16384
    z = int.from_bytes(raw_data[3], "little", signed = True) / 16384
    
    (roll, pitch, yaw) = toEuler(w, x, y, z)
    RPY = [roll, pitch, yaw]
    
    Accelerometer[0] = int.from_bytes(raw_data[4], "little", signed = True) / 2048
    Accelerometer[1] = int.from_bytes(raw_data[5], "little", signed = True) / 2048
    Accelerometer[2] = int.from_bytes(raw_data[6], "little", signed = True) / 2048
    
    Gyroscope[0] = int.from_bytes(raw_data[7], "little", signed = True) / 16
    Gyroscope[1] = int.from_bytes(raw_data[8], "little", signed = True) / 16
    Gyroscope[2] = int.from_bytes(raw_data[9], "little", signed = True) / 16
    print(RPY)
    
def callback_emg(handle, value):
        # print(value)
        raw_data = struct.unpack('>ssssssssssssssss',value)
        global EMG_Count
        global Pose
        if(EMG_Count % 10 == 0):                     # If EMG_Row / has remainder 0 -> 5,10,...
            emg_1[0] = abs(int.from_bytes(raw_data[0], "little", signed = True))
            emg_1[1] = abs(int.from_bytes(raw_data[1], "little", signed = True))
            emg_1[2] = abs(int.from_bytes(raw_data[2], "little", signed = True))
            emg_1[3] = abs(int.from_bytes(raw_data[3], "little", signed = True))
            emg_1[4] = abs(int.from_bytes(raw_data[4], "little", signed = True))
            emg_1[5] = abs(int.from_bytes(raw_data[5], "little", signed = True))
            emg_1[6] = abs(int.from_bytes(raw_data[6], "little", signed = True))
            emg_1[7] = abs(int.from_bytes(raw_data[7], "little", signed = True))
            emg_2[0] = abs(int.from_bytes(raw_data[8], "little", signed = True))
            emg_2[1] = abs(int.from_bytes(raw_data[9], "little", signed = True))
            emg_2[2] = abs(int.from_bytes(raw_data[10], "little", signed = True))
            emg_2[3] = abs(int.from_bytes(raw_data[11], "little", signed = True))
            emg_2[4] = abs(int.from_bytes(raw_data[12], "little", signed = True))
            emg_2[5] = abs(int.from_bytes(raw_data[13], "little", signed = True))
            emg_2[6] = abs(int.from_bytes(raw_data[14], "little", signed = True))
            emg_2[7] = abs(int.from_bytes(raw_data[15], "little", signed = True))
            print(emg_1)
            #print(round(np.mean(emg_1)))
            myostring = str(round(np.mean(emg_1)))
#            arduino.write(bytes(myostring, 'utf-8'))
            
def getIMU():       
    
    myo.subscribe(IMUChar, callback = callback_IMU, indication = False, wait_for_response = True)
    myo.char_write(command, [0x01, 3, 0x02, 0x01, 0x01]) 

#############################################

def getEMG(speed):
    
    if speed == "Slow":
        
        myo.subscribe(emgChar0, callback = callback_emg, indication = False, wait_for_response=True)
    
    elif speed == "Medium":
    
        myo.subscribe(emgChar0, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar1, callback = callback_emg, indication = False, wait_for_response=True)
   
    elif speed == "Fast":
    
        myo.subscribe(emgChar0, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar1, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar2, callback = callback_emg, indication = False, wait_for_response=True)
    
    elif speed == "very_fast": 
        myo.subscribe(emgChar0, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar1, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar2, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar3, callback = callback_emg, indication = False, wait_for_response=True)
   
    myo.char_write(command, [0x01, 3, 0x02, 0x01, 0x00])

#############################################
   
def unlock():
    myo.char_write(command, [0x0a, 1, 0x02])
    
while True:
    try:
        firstRun = True
        Begin()
        getEMG("Slow")
        input("press enter to stop \n")
    finally:
        adapter.stop()
