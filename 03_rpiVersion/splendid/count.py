# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

'''
reads data from sensor,
count peaks for 4 escapes
then insert in the server in MQTT
'''

import time
import paho.mqtt.client as mqtt # use version 1.6.1 (see server version)
import threading
from getmac import get_mac_address as gma
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C

# SETUP -----------------------------------------
# sensors are connected to rPi i2c, no serial, no esp...

bufferSize = 1000 # Number of samples

count={
    "inEscapes":[1,0,0,1],
    "outEscapes":[0,1,1,0],
    "inBees":0,
    "outBees":0
}

# mqtt stuff
broker_address = "titi.etsii.urjc.es"
topic = "splendid/insert/counter"

def on_connect(client, userdata, flags, rc):
    print("MQTT, on_connect")
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)

# ============================================================

# 4 buffers, oner per escape
escapes = [[0]*bufferSize for _ in range(4)]

def insertMqtt(inBees, outBees, mac="00:00:00:00:00:01",timeZone="Europe/Madrid", myMac="00:00:00:00:00:01"):
    payload = "{"+'"mac":"{}","inBees": {},"outBees": {},"timeZone":"{}","user": "{}"' \
        .format(mac,inBees, outBees, timeZone, myMac ) +"}"
    
    print(payload)
    result = client.publish(topic, payload)
    print(result)
    return

def peaks(serie):

    from scipy.signal import find_peaks
    import numpy as np

    # remove noise applying savgol filter
    def suavizar(serie):
        from scipy.signal import savgol_filter
        suave = savgol_filter(serie, window_length=50, polyorder=2)
        return suave
    
    #suave =  suavizar(serie)
    #print(serie)
    peaks, _ = find_peaks(serie, height=.25, prominence=.2, distance=50)
    #print(peaks)
    #print(len(peaks)) # number of found peaks
    return(peaks)

    r={
        "bees": combi.tolist(), # this will be area chart
        "totalBees": len(peaks)
    }
    

def read():
    
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)
    
    global count

    i=0
    start_time = time.time()
    print(start_time)
    while True:
        
            # read from esp
            # electrodes came already multiplied and normalizad 0..1
        try:
           for escape in range(4): #0..3

              x = cap[(escape*2)+1].raw_value/127.0 # 1,3,5,7
              y = cap[(escape*2)+2].raw_value/127.0 # 2,4,6,8
              if x<0:x=0
              if y<0: y=0
              escapes[escape][i] = x*y

        except: pass
        
        # Whe buffer is full counte all the escapes    
        if i>= bufferSize:
            
            end_time = time.time()
            # Calculate elapsed time
            elapsed_time = end_time - start_time
            print("\nElapsed time: ", elapsed_time)
            
            # Count each buffer and acum data
            for bf in range(4):
                try: 
                    bees = peaks(escapes[bf])
                except: 
                    bees=[]

                count["inBees"]+= len(bees) * count["inEscapes"][bf]
                count["outBees"]+=len(bees) * count["outEscapes"][bf]
                print(str(bf),":", str(len(bees)))
            print("\nin",count["inBees"],", out ",count["outBees"])

            i=0 #reset buffer
            start_time = time.time()
        i+=1         



# MQTT: let's go ===============================================

client = mqtt.Client("bcPiZero")
client.on_connect=on_connect
client.connect(broker_address) 
client.loop_start() # Inicio del bucle

# cada x min un hilo vuelca los datos a mqtt
def ejecutar(espera=60):
    global count
    while True:
        insertMqtt(count["inBees"], count['outBees'], gma())
        count['inBees']=0
        count["outBees"]=0
        time.sleep(espera)

'''insert into DB each 5 min'''
insertThread = threading.Thread(target=ejecutar, kwargs={'espera': 300,})
insertThread.start()

read() # read data from sensors
