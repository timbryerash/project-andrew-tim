# Homeowner RPi (Tim)

import paho.mqtt.client as mqtt
import time
import grovepi
import grove_rgb_lcd
import threading
lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    #subscribe to ultrasonicRanger then callback
    client.subscribe("timandrew/door_status")
    client.message_callback_add("timandrew/door_status", door_status_callback)
    #subscribe to button then callback
    client.subscribe("timandrew/doorbell")
    client.message_callback_add("timandrew/doorbell", doorbell_callback)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def door_status_callback(client, userdata, msg):
    door_status = str(msg.payload, "utf-8")
    if door_status == "Motion Detected":
    	with lock:
    		grove_rgb_lcd.setRGB(255,255,255)
    		grove_rgb_lcd.setText_norefresh("Motion          \nDetected        ")
    elif door_status == "SAFETY MODE":
    	with lock:
    		grove_rgb_lcd.setRGB(255,0,0)
    		grove_rgb_lcd.setText_norefresh("SAFETY MODE     \nACTIVATED       ")
    	with lock:
    		grovepi.digitalWrite(buzzer, 1)
    		time.sleep(0.1)
    		grovepi.digitalWrite(buzzer, 0)
    else:
    	with lock:
    		grove_rgb_lcd.setRGB(255,255,255)
    		grove_rgb_lcd.setText_norefresh("Front Door      \nSecure          ")

def doorbell_callback(client, userdata, msg):
    with lock:
    		grove_rgb_lcd.setRGB(0,255,0)
    		grove_rgb_lcd.setText_norefresh("Doorbell        \nRung            ")
    		grovepi.digitalWrite(buzzer, 1)
    		time.sleep(0.1)
    		grovepi.digitalWrite(buzzer, 0)
    time.sleep(1)

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    #initiate ports
    buzzer = 2
    button = 4

    grovepi.pinMode(buzzer, "OUTPUT")
    grovepi.pinMode(button,"INPUT")

    # Initiate in locked mode
    lock_status = 0

    #splashscreen
    with lock:
        grove_rgb_lcd.setRGB(255,255,255)
        grove_rgb_lcd.setText("Tim & Andrew\nHomeowner")
        time.sleep(2)
        grove_rgb_lcd.setText("")

    while True:
        with lock:
            buttonvalue = grovepi.digitalRead(button) #check button reading
        if buttonvalue:
        	if lock_status:
        		lock_status = 0
        		client.publish("timandrew/homeowner_button", "Locked")
        	else:
        		lock_status = 1
        		client.publish("timandrew/homeowner_button", "Unlocked")
        time.sleep(1)
