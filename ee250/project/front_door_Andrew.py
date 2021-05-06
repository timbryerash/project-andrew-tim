import sys
import time
import grovepi
import grove_rgb_lcd
import threading
from grove_rgb_lcd import *

ultrasonic_ranger = 3

full_angle = 300
adc_ref = 5
grove_vcc = 5
button = 2

grovepi.pinMode(button,"INPUT")

# state = 0 --> safe/locked
# state = 1 --> motion detected
# state = 2 --> safety mode
# state = 3 --> unlocked
# state = 4 --> ringing doobell / waiting for access

state = 0
timer = 5

while True:
    
    # Read angle value from potentiometer
    sensor_value = grovepi.ultrasonicRead(ultrasonic_ranger)
    
    # state 1 --> motion detected 
    if (sensor_value <= 30 and state is 0):
        while (timer >=  0):
            state = 1
            setRGB(255,0,0)
            setText_norefresh("" + "OBJECT DETECTED!" + "\nSAFE MODE IN %ds" %timer)
            timer = timer - 1
            time.sleep(0.4)
        
    # state 2 --> safety mode
    if (timer is -1 and state is 1):
        state = 2
        while (state is 2):
            setRGB(255,255,0)
            grove_rgb_lcd.setText("SAFETY MODE \nWaiting for resp")
            time.sleep(10)
        
    # state 4 --> waiting for access
    elif (grovepi.digitalRead(button) is 1):
        state = 4
        setRGB(255,255,0)
        grove_rgb_lcd.setText("")
        setText_norefresh("Ringing doorbell \nWaiting for resp")
        time.sleep(2)
        
    else:
        state = 0
        setRGB(0,255,0)
        setText_norefresh("SENSOR ACTIVE   " + "" + "\n%dcm             " %sensor_value)
        time.sleep(0.2)
        
    

   