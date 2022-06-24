import board
import busio
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit


i2c = busio.I2C(board.SCL, board.SDA)
#hat = adafruit_pca9685.PCA9685(i2c)
pca = PCA9685(i2c)
pca.frequency = 500

kit = ServoKit(channels = 16)

#servo1 = servo.Servo(pca.channels[0])  # Top Left
servo1 = servo.Servo(pca.channels[0], min_pulse=550, max_pulse=2650)
servo2 = servo.Servo(pca.channels[1], min_pulse=700, max_pulse=2650)
servo3 = servo.Servo(pca.channels[2])
servo4 = servo.Servo(pca.channels[3])  # Bottom Middle
servo5 = servo.Servo(pca.channels[4], min_pulse=550, max_pulse=2650)
servo6 = servo.Servo(pca.channels[5], min_pulse=600, max_pulse=2650)
servo7 = servo.Servo(pca.channels[6], min_pulse=550, max_pulse=2400)  # Top Right

servo1.angle = 10
servo2.angle = 10

servo6.angle = 150
servo7.angle= 150
time.sleep(1)
servo1.angle = 170





