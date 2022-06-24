
import pygatt
import logging
import binascii     #Byte array to Hex
import time
import struct
import math







##################################################
# Insantiate Myo and Define UUID Characteristics #
##################################################

MAC = "F0:3E:E5:F2:F1:CD"

uuid_vendor = "d5060001-a904-deb9-4748-2c7f4a124842"

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

unknown = uuid1 + "0106" + uuid2

adapter = pygatt.GATTToolBackend()
logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

adapter.start()
myo = adapter.connect(MAC)

def callback(handle, value):
    print(handle)
    print(value)

try:
    myo.subscribe(unknown, callback)
    myo.char_write(command, [0x01, 3, 0x02, 0x03, 0x01]) 
finally:
    adapter.stop()
     
 
 
