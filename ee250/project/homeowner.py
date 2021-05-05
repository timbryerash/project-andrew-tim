# Homeowner RPi (Tim)

# BELOW IS CODE FROM LAB 5

import paho.mqtt.client as mqtt
import time
import grovepi
import grove_rgb_lcd
import threading
lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    #subscribe to lcd then callback
    client.subscribe("timandrew/lcd")
    client.message_callback_add("timandrew/lcd", lcdcallback)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def lcdcallback(client, userdata, msg):
    keyvalue = str(msg.payload, "utf-8") #w, a, s, or d
    print(keyvalue)
    with lock:
        grove_rgb_lcd.setText_norefresh(f"{keyvalue}") #display key on lcd
        if keyvalue == "w":
            grove_rgb_lcd.setRGB(255,255,255) #make white
        if keyvalue == "a":
            grove_rgb_lcd.setRGB(255,0,0) #make red
        if keyvalue == "s":
            grove_rgb_lcd.setRGB(0,255,0) #make green
        if keyvalue == "d":
            grove_rgb_lcd.setRGB(0,0,255) #make blue

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    #initiate ports
    button = 2

    grovepi.pinMode(button,"INPUT")

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
            client.publish("timandrew/button", "Button pressed!") #if button is pressed, publish string to button topic

        time.sleep(1)
