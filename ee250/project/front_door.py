# Front Door RPi (Andrew)

lock_status = "Locked"

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
    global lock_status
    lock_status = str(msg.payload, "utf-8")
    print("Door status: " + lock_status)
            
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
    
    grovepi.pinMode(button,"INPUT")

    # state = 0 --> Sensor active
    # state = 1 --> Motion detected
    # state = 2 --> Safety mode

    state = 0
    timer = 20

    #splashscreen
    with lock:
    	grove_rgb_lcd.setRGB(255,255,255)
    	grove_rgb_lcd.setText("Tim & Andrew\nFront Door")
    	time.sleep(2)
    	grove_rgb_lcd.setText("")

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
            setRGB(0,0,255)
            setText_norefresh("Ringing doorbell\nWaiting for resp")
            time.sleep(2)
                
    if lock_status == "Locked":    
        # state 1 --> motion detected
        if (sensor_value <= 30 and state == 0):
            state = 1
            timer = 20
            while (state == 1):
                client.publish("timandrew/door_status", "Motion Detected")
                sensor_value = grovepi.ultrasonicRead(ultrasonic_ranger)
                with lock:
                    setRGB(255,165,0)
                    setText_norefresh("" + "OBJECT DETECTED!" + "\nSAFE MODE IN %d" %timer + "s ")
                    timer = timer - 1
                    if(lock_status == "Unlocked" or timer < 0):
                        state = 2
                        break
                    if(sensor_value > 30):
                        setRGB(255,69,0)
                        setText_norefresh("Alarm           \nDeactivated     ")
                        time.sleep(2)
                        state = 0 
                        break;
                    time.sleep(0.4)
            
        # state 2 --> safety mode
        elif (timer is -1 and state is 2):
            while (state is 2):
                client.publish("timandrew/door_status", "SAFETY MODE")
                with lock:
                    setRGB(255,0,0)
                    grove_rgb_lcd.setText_norefresh("SAFETY MODE     \nStatus: "+ lock_status + "  ")
                    if(lock_status == "Unlocked"):
                        break
        else:
            #state 0 --> sensor active
            client.publish("timandrew/door_status", "NO MOTION")
            with lock:
                setRGB(255,255,255)
                grove_rgb_lcd.setText_norefresh("SENSOR ACTIVE   \nStatus: "+ lock_status + "  ")
                    
    elif lock_status == "Unlocked":
        #reinitialize 
        state = 0
        timer = 20
        with lock:
            setRGB(0,255,0)
            grove_rgb_lcd.setText_norefresh("Door is Open    \nStatus: " + lock_status)
            
                

                
    
            




















