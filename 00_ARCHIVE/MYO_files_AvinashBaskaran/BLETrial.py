import board
import busio
import pygatt
import logging
import binascii     #Byte array to Hex
import time
import struct
import math as m
import numpy as np
import scipy.io as sp
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit

#############################################
## Initialize Servos and Set initial Angle ##
#############################################

i2c = busio.I2C(board.SCL, board.SDA)
#hat = adafruit_pca9685.PCA9685(i2c)
pca = PCA9685(i2c)
pca.frequency = 500

kit = ServoKit(channels = 16)

firstRun = True
rollSync = 0
sync = 0

EMG_Count = 0
Moving_Matrix = np.zeros((10,8))
Max_Moving_Matrix = np.zeros((10,8))
Pose = 0                        # Global Pose Value. Setting this will set Servos

oddMatrix = sp.loadmat('/home/pi/Desktop/OddsMatrix.mat') # Odds Matrix
OddMat = np.array(oddMatrix['finalMatrix'])
# F R P O
F = 0
R = 1
P = 2
O = 3
oddsIndexF = np.zeros((8,8))
oddsIndexR = np.zeros((8,8))
oddsIndexO = np.zeros((8,8))
oddsIndexP = np.zeros((8,8))

# Odds for Fist, column 3 / c5 = 2.2 ----> OddMat[ F, 3, 5, 4]
# need to create matrix of maxes / maxes, m.floor(num * 2)

### Bins ###
# 0 -> .5 = 0
#.5 -> 1 = 1
# 1 ->1.5 = 2
# 1.5 -> 2 = 3
# 2 -> 2.5 = 4
#2.5 -> 3 = 5
# 3 -> 3.5  = 6
# 3.5 -> 4 = 7
# 4 -> 4.5 = 8
# 4.5 -> 5 = 9
# 5 -> 5.5 = 10
# 5.5 -> 6 = 11
# ...
# 9.5 -> 10 = 20




########## Instantiate Servos and Declare Constants ################

IndexServo = servo.Servo(pca.channels[6], min_pulse=550, max_pulse=2650)
MiddleServo = servo.Servo(pca.channels[1], min_pulse=550, max_pulse=2650)
RingServo = servo.Servo(pca.channels[0], min_pulse=550, max_pulse=2650)
PinkieServo = servo.Servo(pca.channels[5], min_pulse=550, max_pulse=2650)
ThumbServo = servo.Servo(pca.channels[2], min_pulse=550, max_pulse=2650)
ThumbBaseServo = servo.Servo(pca.channels[4], min_pulse=550, max_pulse=2650)

speed = .02
Index_Max = 175
Pinkie_Max = 175
Middle_Max = 5
Ring_Max = 5
Thumb_Max = 175
TumbBase_Max = 175

Index_Min = 5
Pinkie_Min = 5
Middle_Min = 175
Ring_Min = 175
Thumb_Min = 175
ThumbBase_Min = 175

Index_Relaxed = 90
Pinkie_Relaxed = 90
Middle_Relaxed = 90
Ring_Relaxed = 90
Thumb_Relaxed = 175
ThumbBase_Relaxed = 175

Posed = [False, False, False, False, False, False, False]
# [All Index Middle Ring Pinkie Thumb ThumbBase]
Angles = [0, 0, 0, 0, 0, 0, 0]  # 

######################################################

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
#logging.basicConfig()
#logging.getLogger('pygatt').setLevel(logging.DEBUG)

adapter.start()
myo = adapter.connect(MAC)
 

#############################################
##### Inizializing Arrays for later use #####
#############################################

Accelerometer = [0, 0, 0]
Gyroscope = [0, 0, 0]
conversion = 180 / m.pi

emg_1 = [0,0,0,0,0,0,0,0]
emg_2 = [0,0,0,0,0,0,0,0]
#############################################
def Begin():
    global Posed
    global Angles
    IndexServo.angle  = Index_Min
    MiddleServo.angle = Middle_Min
    RingServo.angle = Ring_Min
    PinkieServo.angle = Pinkie_Min
    ThumbServo.angle = Thumb_Min
    ThumbBaseServo.angle = ThumbBase_Min

    Angles = [Index_Min, Middle_Min, Ring_Min, Pinkie_Min, Thumb_Min, ThumbBase_Min, 0] 
    Posed = [False, False, False, False, False, False, False]
    
    
def getBattery():

    battery = myo.char_read(uuid_battery)
    batteryOutput = int(binascii.hexlify(battery),16)
    print(batteryOutput)

#############################################

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

    ##### Servo control from IMU
#     if firstRun == True:          # Need Original Roll to be servo.angle = 90
#         rollSync = roll
#         firstRun = False
#         servo0.angle = 90
#         angle0 = int(servo0.angle)
#         print(angle0)
#         if angle0 > 90:
#              while angle0 > 90:
#                 angle0 = angle0 - 1
#                 servo0.angle = angle0
#     
#                 time.sleep(.05)
#         elif angle0 < 90:
#              while angle0 < 90:
#                 angle0 = angle0 + 1
#                 servo0.angle = angle0
#     
#                 time.sleep(.05)        
#     
#     rollDiff = roll - rollSync
#     servo0.angle = 90 - rollDiff
    
    print(RPY)
    
#############################################

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
     
            Row = int(EMG_Count / 10)
            (Avg,Max) = Moving_Average(Row,emg_1)   # Send # and EMG 1, get moving average and maximums
            newPose = Classifier2(Avg)
            oldPose = Pose
            setPose(newPose,oldPose)
            
            if(EMG_Count == 90):                    # Reset
                EMG_Count = 0
                
            else:
                EMG_Count = EMG_Count + 1
        else:
            EMG_Count = EMG_Count + 1
       # print(emg[:8])
       # print(emg[8:])
############################################

def Classifier2(mat):
    row = 0
    col = 1
    oddF = 1
    oddR = 1
    oddP = 1
    oddO = 1
    while(row <= 6):
        col = row +1
        while(col <= 7):
            
            if(int(mat[col]) != 0):
                index = m.floor((mat[row] / mat[col])*2)
                if(index <20):
                    
                    oddF = OddMat[F,row,col,index] * oddF
                    oddR = OddMat[R,row,col,index] * oddR
                    oddO = OddMat[O,row,col,index] * oddO
                    oddP = OddMat[P,row,col,index] * oddP
            
            col = col+1
        row = row+1
    odd = [oddF, oddR, oddP, oddO]
    maxNum = np.max(odd)  
    if maxNum == oddF:
        Pose = 1
        print("fist")
    elif maxNum == oddP:
        Pose = 2
        print("peace")
    elif maxNum == oddO:
        Pose = 3
        print("open")
    elif maxNum == oddR:
        Pose = 4
        print("relax")
    elif maxNum == 0:
        print("Zero")
    else:
        Pose = 0
        print("error")
    return Pose







###############################################

def setPose(newPose,oldPose):               # Fist = 1
    global Angles                           # Peace = 2
    global Posed                            # Open = 3
    global Pose                             # Relaxed = 4
                                            # Unknown = 5
    if(newPose == oldPose):
        Posed = [True, True, True, True, True, True, True]
    else:
        Posed = [False, False, False, False, False, True, True]
        (Index, Middle, Ring, Pinkie, Thumb, ThumbBase) = getAngles()
        if(newPose == 1):
            setAllMax(Index, Middle, Ring, Pinkie, Thumb, ThumbBase)
            Pose = 1
            
        elif(newPose == 3):
            setAllMin(Index, Middle, Ring, Pinkie, Thumb, ThumbBase)
            Pose = 3
        
        elif(newPose == 4):
            setRelax()
            Pose = 4
####################################################################3            
            
def getAngles():
    global Angles
    Index = Angles[0]
    Middle = Angles[1] 
    Ring = Angles[2]
    Pinkie = Angles[3]
    Thumb = Angles[4]
    ThumbBase = Angles[5]
    return (Index, Middle, Ring, Pinkie, Thumb, ThumbBase)

################################################################33

def setRelax():
    global Angles
    global Posed
    while(Posed[0] != True):
        Index = Angles[0]
        Middle = Angles[1] 
        Ring = Angles[2]
        Pinkie = Angles[3]
        Thumb = Angles[4]
        ThumbBase = Angles[5]
        
        if (Index == Index_Relaxed):
            Posed[1] = True
            Angles[0] = Index_Relaxed
        else:
            if(Index > Index_Relaxed):
                Sign = -1
            else:
                Sign = 1
            IndexServo.angle = Angles[0] + Sign
            Angles[0] = int(Angles[0] + Sign)
            
        if (Pinkie == Pinkie_Relaxed):
            Posed[4] = True
            Angles[3] = Pinkie_Relaxed
        else:
            if(Pinkie > Pinkie_Relaxed):
                Sign = -1
            else:
                Sign = 1
            PinkieServo.angle = Angles[3] + Sign
            Angles[3] = int(Angles[3] + Sign)
        
        if (Middle == Middle_Relaxed):
            Posed[2] = True
            Angles[1] = Middle_Relaxed
        else:
            if(Middle > Middle_Relaxed):
                Sign = -1
            else:
                Sign = 1
            MiddleServo.angle = Angles[1] + Sign
            Angles[1] = int(Angles[1] + Sign)
            
        if (Ring == Ring_Relaxed):
            Posed[3] = True
            Angles[2] = Ring_Relaxed
        else:
            if(Ring > Ring_Relaxed):
                Sign = -1
            else:
                Sign = 1
            RingServo.angle = Angles[2] + Sign
            Angles[2] = int(Angles[2] + Sign)
        print(Posed)
        if(Posed[1] == True and Posed[2] == True and Posed[3] == True and Posed[4] == True):
            Posed[0] = True
        else:
            time.sleep(speed)            
            
            
###########################################################################    
    
def setAllMax(Index, Middle, Ring, Pinkie, Thumb, ThumbBase):
    global Angles
    global Posed
    while(Posed[0] != True):
        Index = Angles[0]
        Middle = Angles[1] 
        Ring = Angles[2]
        Pinkie = Angles[3]
        Thumb = Angles[4]
        ThumbBase = Angles[5]
        print(Posed)
        if (Index == Index_Max):
            Posed[1] = True
            Angles[0] = Index_Max
        else:
            IndexServo.angle = Angles[0] + 1
            Angles[0] = int(Angles[0] + 1)
        
        if (Pinkie == Pinkie_Max):
            Posed[4] = True
            Angles[3] = Pinkie_Max
        else:
            PinkieServo.angle = Angles[3] + 1
            Angles[3] = int(Angles[3] + 1)
            
        if (Middle == Middle_Max):
            Posed[2] = True
            Angles[1] = Middle_Max
        else:
            MiddleServo.angle = Angles[1] - 1
            Angles[1] = int(Angles[1] - 1)
        
        if (Ring == Ring_Max):
            Posed[3] = True
            Angles[2] = Ring_Max
        else:
            RingServo.angle = Angles[2] - 1
            Angles[2] = int(Angles[2] - 1)
        
        if(Posed[1] == True and Posed[2] == True and Posed[3] == True and Posed[4] == True):
            Posed[0] = True
        else:
            time.sleep(speed)
        
 ##########################################
            
def setAllMin(Index, Middle, Ring, Pinkie, Thumb, ThumbBase):
    global Angles
    global Posed
    while(Posed[0] != True):
        Index = Angles[0]
        Middle = Angles[1] 
        Ring = Angles[2]
        Pinkie = Angles[3]
        Thumb = Angles[4]
        ThumbBase = Angles[5]
        
        if (Index == Index_Min):
            Posed[1] = True
            Angles[0] = Index_Min
        else:
            IndexServo.angle = Angles[0] - 1
            Angles[0] = int(Angles[0] - 1)
        
        if (Pinkie == Pinkie_Min):
            Posed[4] = True
            Angles[3] = Pinkie_Min
        else:
            PinkieServo.angle = Angles[3] - 1
            Angles[3] = int(Angles[3] - 1)
            
        if (Middle == Middle_Min):
            Posed[2] = True
            Angles[1] = Middle_Min
        else:
            MiddleServo.angle = Angles[1] + 1
            Angles[1] = int(Angles[1] + 1)
        
        if (Ring == Ring_Min):
            Posed[3] = True
            Angles[2] = Ring_Min
        else:
            RingServo.angle = Angles[2] + 1
            Angles[2] = int(Angles[2] + 1)
        if(Posed[1] == True and Posed[2] == True and Posed[3] == True and Posed[4] == True):
            Posed[0] = True
        else:
            time.sleep(speed)
    return 
    
#############################################

def Moving_Average(rNum,Mat1):
    
       Moving_Matrix[rNum-1] = Mat1
       
       #Average_Matrix = np.mean(Moving_Matrix,axis=0)
       
       Max_Matrix = np.max(Moving_Matrix, axis=0)
       Max_Moving_Matrix[rNum-1] = Max_Matrix
   
       Average_Matrix = np.mean(Max_Moving_Matrix,axis=0)
       
       return (Average_Matrix,Max_Matrix)
       
        
#############################################

def Classifier(Maxes):
    ## Poses ##
    # Fist = 1
    # Peace = 2
    # Open = 3
    # Relaxed = 4
    (oddsF1, oddsR1, oddsP1, oddsO1) = Channel_1(Maxes[0])
    (oddsF3, oddsR3, oddsP3, oddsO3) = Channel_3(Maxes[2])
    (oddsF6, oddsR6, oddsP6, oddsO6) = Channel_6(Maxes[5])
    (oddsF8, oddsR8, oddsP8, oddsO8) = Channel_8(Maxes[7])
    matrix1 = ([oddsF1, oddsR1, oddsP1, oddsO1],[oddsF3, oddsR3, oddsP3, oddsO3], [oddsF6, oddsR6, oddsP6, oddsO6], [oddsF8, oddsR8, oddsP8, oddsO8]) 
    
    
    oddsF = oddsF1 * oddsF3 * oddsF6 * oddsF8
    oddsR = oddsR1 * oddsR3 * oddsR6 * oddsR8
    oddsP = oddsP1 * oddsP3 * oddsP6 * oddsP8
    oddsO = oddsO1 * oddsO3 * oddsO6 * oddsO8
    
    odds = [oddsF, oddsR, oddsP, oddsO]
    maxNum = np.max(odds)  
    if maxNum == oddsF:
        Pose = 1
        print("fist")
    elif maxNum == oddsP:
        Pose = 2
        print("peace")
    elif maxNum == oddsO:
        Pose = 3
        print("open")
    elif maxNum == oddsR:
        Pose = 4
        print("relax")
    else:
        Pose = 0
        print("error")
    return Pose

############################################

def Channel_1(num): 
    if num >= 50:
        oddsF1 = .975
        oddsR1 = 0
        oddsP1 = 0
        oddsO1 = .025
    elif num >= 15 and num < 50:
        oddsF1 = .101
        oddsR1 = 0
        oddsP1 = .435
        oddsO1 = .464
    else:
        oddsF1 = 0
        oddsR1 = .796
        oddsP1 = .132
        oddsO1 = .072
    return oddsF1, oddsR1, oddsP1, oddsO1
############################################

def Channel_3(num): 
    if num >= 40:
        oddsF3 = .617
        oddsR3 = 0
        oddsP3 = .388
        oddsO3 = 0
    elif num >= 15 and num < 40:
        oddsF3 = .046
        oddsR3 = 0
        oddsP3 = .462
        oddsO3 = 0.491
    else:
        oddsF3 = .0
        oddsR3 = .624
        oddsP3 = .01
        oddsO3 = .366
    return oddsF3, oddsR3, oddsP3, oddsO3
############################################

def Channel_6(num): 
    if num >= 25:
        oddsF6 = 1
        oddsR6 = 0
        oddsP6 = 0
        oddsO6 = 0
    elif num >= 10 and num < 25:
        oddsF6 = .535
        oddsR6 = .109
        oddsP6 = 0
        oddsO6 = .357
    else:
        oddsF6 = .002
        oddsR6 = .35
        oddsP6 = .39
        oddsO6 = .259
    return oddsF6, oddsR6, oddsP6, oddsO6
############################################

def Channel_8(num):
    if num >= 60:
        oddsF8 = .456
        oddsR8 = 0
        oddsP8 = .027
        oddsO8 = .517
    elif num >= 40 and num < 60:
        oddsF8 = .302
        oddsR8 = 0
        oddsP8 = .027
        oddsO8 = .671
    elif num >= 25 and num < 40:
        oddsF8 = .447
        oddsR8 = 0
        oddsP8 = .263
        oddsO8 = .289
    else:
        oddsF8 = .131
        oddsR8 = .462
        oddsP8 = .405
        oddsO8 = .003
    return oddsF8, oddsR8, oddsP8, oddsO8
#############################################
        
def callback_pose(handle,value):
    
    global sync
    
    print("sub")
    if value[0] == 3:
        if value[1] == 0:
            servo0.angle = 30
        #    servo1.angle = 30
            print("Rest")
        elif value[1] == 1:
            servo0.angle = 90
           # servo1.angle = 90
            print("Fist")

        elif value[1] == 2:
            print("Wave In")
        elif value[1] == 3:
            print("Wave Out")
        elif value[1] == 4:
            print("Fingers Spread")
            servo0.angle = 0
      #      servo1.angle = 0
        elif value[1] == 5:
            print("Double Tap")
        else:
            print("Pose Unknown")
    elif value[0] == 4:
        print("Unlocked")
        
    elif value[0] == 5:
        print("Locked")
        
    elif value[0] == 1:
        print("Synced")
        sync = 1
        
    elif value[0] == 2:
        print("Unsynced. Retry Sync")
        sync = 2
#         myo.char_write(command, [0x03, 1, 0x03], False)
#         
#         
#         
#         myo.char_write(command, [0x0a, 1, 0x00], False)
#         myo.char_write(command, [0x0a, 1, 0x02], False)
#         
#         myo.char_write(command, [0x01, 3, 0x00, 0x03, 0x02], False)
#        
#         myo.char_write(command, [0x03, 1, 0x03], False)
        
    elif value[0] == 6:
        if value[1] == 1:
            print("Failed. Too Hard")
        else:
            ("Failed, unknown")
    
    else:
        print("Unknown charactistic change")    
#############################################     
        
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
    
    elif speed == "I want to burn my house down and I want the Pi to start the fire":
    
        myo.subscribe(emgChar0, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar1, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar2, callback = callback_emg, indication = False, wait_for_response=True)
        myo.subscribe(emgChar3, callback = callback_emg, indication = False, wait_for_response=True)
   
    myo.char_write(command, [0x01, 3, 0x02, 0x01, 0x00])

#############################################

def getPose():
    
    myo.subscribe(pose, callback = callback_pose, indication = True, wait_for_response = True)
    myo.char_write(command, [0x01, 3, 0x02, 0x03, 0x01])

#############################################
    
def unlock():
    myo.char_write(command, [0x0a, 1, 0x02])
    

try:    
        
#     myo.char_write(command, [0x01, 3, 0x00, 0x01, 0x01])
    firstRun = True
    Begin()
    getEMG("Slow")
#     myo.subscribe(pose, callback = callback_pose, indication = True, wait_for_response = True)
# 

    
   #
#     getPose()
    #getEMG("Slow")
   # myo.subscribe(pose, callback = callback_pose, indication = False, wait_for_response = True)
  #  myo.char_write(command, [0x01, 3, 0x02, 0x03, 0x01])
   # getEMG("Slow")


    
    

    input("press enter to stop \n")
finally:
    

    adapter.stop()





