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
    lock_status = str(msg.payload, "utf-8")
    print(lock_status)
    #if lock_status == "Unlocked":
     #   with lock:
      #      setRGB(0,100,250)
       #     setText_norefresh("WELCOME HOME")
        #    time.sleep(2)
            
if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    #initiate ports
    ultrasonic_ranger = 3
    button = 2
    full_angle = 300
    adc_ref = 5
    grove_vcc = 5
    lock_status = "Locked"
    
    grovepi.pinMode(button,"INPUT")

    # state = 0 --> Sensor active
    # state = 1 --> Motion detected
    # state = 2 --> Safety mode

    state = 0
    timer = 20

while True:
    
    with lock:
        # check if button is pressed
        button_value = grovepi.digitalRead(button)
        
    with lock:
        # Read angle value from potentiometer
        sensor_value = grovepi.ultrasonicRead(ultrasonic_ranger)
        client.publish("timandrew/motion_sensor",sensor_value)
        
    if button_value: 
        client.publish("timandrew/doorbell", "Doorbell Rung")
        with lock:
            setRGB(255,255,0)
            grove_rgb_lcd.setText("")
            setText("Ringing doorbell\nWaiting for resp")
            time.sleep(2)
        
    # if the door is locked
    #if lock_status is "Locked":
        
    # state 1 --> motion detected
    if (sensor_value <= 30 and state is 0):
        state = 1
        while (timer >=  0):
            client.publish("timandrew/door_status", "Motion Detected")
            with lock:
                setRGB(255,0,0)
                setText_norefresh("" + "OBJECT DETECTED!" + "\nSAFE MODE IN %ds" %timer)
                timer = timer - 1
                time.sleep(0.4)
        
    # state 2 --> safety mode
    elif (timer is -1 and state is 1):
        state = 2
        while (state is 2):
            client.publish("timandrew/door_status", "SAFETY MODE")
            with lock:
                setRGB(255,255,0)
                grove_rgb_lcd.setText("SAFETY MODE \nWaiting for resp")
                time.sleep(10)
                
    #state 0 --> sensor active
    else:
        state = 0
        while(state = 0):
            client.publish("timandrew/door_status", "SAFETY MODE")
            with lock:
                setRGB(0,255,0)
                setText_norefresh("SENSOR ACTIVE   ")
                

                
    
            










