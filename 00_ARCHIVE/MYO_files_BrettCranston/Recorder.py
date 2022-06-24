import board
import busio
import adafruit_pca9685
import csv
import pygatt
import logging
import binascii     #Byte array to Hex
import time
import struct
import math
import numpy as np


from adafruit_servokit import ServoKit

#############################################
## Initialize Servos and Set initial Angle ##
#############################################

i2c = busio.I2C(board.SCL, board.SDA)
hat = adafruit_pca9685.PCA9685(i2c)

hat.frequency = 60

kit = ServoKit(channels = 16)

servo0 = kit.servo[0]
servo0.set_pulse_width_range(600,2500)
firstRun = True
rollSync = 0
sync = 0

EMG_Count = 0
Avg_Mat = np.zeros((250,8))
Pose = 0                        # Global Pose Value. Setting this will set Servos
# Commands:
# servo0.angle = 90
# servo0.actuation_range = 160
# servo0.set_pulse_width_range(min, max)





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
logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

adapter.start()
myo = adapter.connect(MAC)
emg_1 = [0,0,0,0,0,0,0,0]
emg_2 = [0,0,0,0,0,0,0,0]
#############################################

def callback_emg(handle, value):
    # print(value)
    raw_data = struct.unpack('<ssssssssssssssss',value)
    global EMG_Count
   # if(EMG_Count % 5 == 0):                     # If EMG_Row / has remainder 0 -> 5,10,...
    
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
    
            
    Row = int(EMG_Count / 5)
       # Avg = Moving_Average(emg_1)   # Send # and EMG 1
    Avg_Mat[Row] = emg_1[:8]
    print(emg_1[:8])


    EMG_Count = EMG_Count + 1
  #  else:
     #   EMG_Count = EMG_Count + 1
       # print(emg_1[:8])
       # print(emg[8:])
       
#############################################

def Moving_Average(Mat1):
    
    Average_Matrix = np.mean(Mat1,axis=0)
      
    return Average_Matrix
      
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
    
    elif speed == "I want to burn my house down and I want the Pi to start the fire":
    
        myo.subscribe(emgChar0, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar1, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar2, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar3, callback = callback_emg, indication = False, wait_for_response=True)

    myo.char_write(command, [0x01, 3, 0x02, 0x01, 0x00])

############


try:
#     myo.char_write(command, [0x01, 3, 0x00, 0x01, 0x01])
    firstRun = True
    getEMG("Slow")

    input("press enter to stop \n")
  #  with open('pose_data.csv', 'w', newline='') as csvfile:
    np.savetxt("./PoseData/Open_D.csv", Avg_Mat, fmt = '%d', delimiter=" ")
finally:
    adapter.stop()

   
       
       
       


