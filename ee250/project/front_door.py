# Front Door RPi (Andrew)

# BELOW IS CODE FROM LAB 5

import paho.mqtt.client as mqtt
import time
import grovepi
import grove_rgb_lcd
import threading
from grove_rgb_lcd import *
lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    #subscribe to homeowner_button then callback
    client.subscribe("timandrew/homeowner_button")
    client.message_callback_add("timandrew/homeowner_button", homeowner_button_callback)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def homeowner_button_callback(client, userdata, msg):
    if lock_status:
        lock_status = 0
    else:
    	lock_status = 1

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    #initiate ports
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
    lock_status = 0 # Initiate locked
    timer = 5
    
while True:
    
    with lock:
        # Read angle value from potentiometer
        sensor_value = grovepi.ultrasonicRead(ultrasonic_ranger)
    
    # state 1 --> motion detected 
    if (sensor_value <= 30 and state is 0):
        while (timer >=  0):
            state = 1
            with lock:
                setRGB(255,0,0)
                setText_norefresh("" + "OBJECT DETECTED!" + "\nSAFE MODE IN %ds" %timer)
                timer = timer - 1
                time.sleep(0.4)
        
    # state 2 --> safety mode
    if (timer is -1 and state is 1):
        state = 2
        while (state is 2):
            with lock:
                setRGB(255,255,0)
                grove_rgb_lcd.setText("SAFETY MODE \nWaiting for resp")
                time.sleep(10)
        
    # state 4 --> waiting for access
    elif (grovepi.digitalRead(button) is 1 and state is 0):
        with lock:
            setRGB(255,255,0)
            grove_rgb_lcd.setText("")
            setText("Ringing doorbell \nWaiting for resp")
            time.sleep(2)
            
    else:
        state = 0
        with lock:
            setRGB(0,255,0)
            setText_norefresh("SENSOR ACTIVE   " + "" + "\n%dcm             " %sensor_value)
            time.sleep(0.2)


