'''
scp contarRpi.py tadu@192.168.1.133/home/tadu/splendid/contarRpi.py 
'''

from datetime import datetime
import time
import threading
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C 

#para contar
# pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt # use version 1.6.1 (see server version)

import peaksLib


def on_connect(client, userdata, flags, rc):
    print("MQTT, on_connect")
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


def insertMqtt(inBees, outBees, 
               mac="00:00:00:00:00:00",
               timeZone="Europe/Madrid", 
               myMac="00:00:00:00:00:01"):

    payload = "{"+'"mac":"{}","inBees": {},"outBees": {},"timeZone":"{}","user": "{}"' \
        .format(mac,inBees, outBees, timeZone, myMac ) +"}"

    print(payload)
    result = client.publish(topic, payload)
    print("Result: ", result)
    return

#======================================================


# Aquí leer del cap1188 --------------
def leer(  ):

    print("\nLeer")

    global ys
    global lock
    global total # Array con todas las muestras
    global totaBees

    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)

    cap.averaging = 4 #verages = (1, 2, 4, 8, 16, 32, 64, 128)
    cap.sample="1.28ms" #("320us", "640us", "1.28ms", "2.56ms")
    cap.cycle="35ms" # "35ms", "70ms", "105ms", "140ms"
     
    print(f"Sensor Initial Configuration Values: {cap.averaging, cap.sample, cap.cycle}")
   
    # Recibo las muestras
    while True:
   
        try:
           for escape in range(8): # Mando todos aunque solo use 4
               val = (127+cap.delta_count(escape+1))/255.0
               lock.acquire()
               ys[escape].append(val)
               ys[escape].pop(0)
               lock.release() 

        except Exception as e: print(e)


def contar():
    global current
    global ys
    global lock
    global totalBees
    
    lastFound = [0]*8  # picos entcontrados en la ventana anterior
    
    def contarEscape(y, total, last=0, pitar = False):
        # buscar las abejas (find peaks)
        try:  
            #print(y[:20])
            _, peaks = peaksLib.findPeaks(y)
            #bees = peaksLib.drawPeaks(peaks, len(y)) # bees es el array

            nBees = len(peaks) # number of bees on last window (2000 valores)
            #print(peaks)
            # acumula los pico encontrados
            inc = nBees-last
            #print("Incremento: ",inc)
            if inc > 0 : 
                total+= inc
                if pitar: pass
            last = nBees

        except Exception as e: print("Error:",e)
        
        return total, last
    
    
    while True:

        time.sleep(.25)
        for escape in range(8):

            lock.acquire()
            copia = ys[escape].copy()
            lock.release()
            totalBees[escape], lastFound[escape] = contarEscape(
                copia,
                totalBees[escape],
                lastFound[escape], 
                escape==current                
                )
        #print(totalBees)

'''Inserta en el servidor cada 5 min y resetea'''    
def insertar():

    global totalBees #array con conteos acumulados
    count={
        "outEscapes": [0,1,0,1,0,0,0,0],
        "inEscapes":  [1,0,1,0,0,0,0,0],
        "inBees":0,
        "outBees":0
    }
    print("insertar en BD")
    while True:
        time.sleep(60) # produccion: 300, 5 min

        # entran o salen?
        print("totalBees")
        print(totalBees)
        for i in range(8):
            if (count['outEscapes'][i]==1): count['outBees']+=totalBees[i]
            if (count['inEscapes'][i]==1): count['inBees']+=totalBees[i]

        #enviar mqtt
        print(count)
        insertMqtt(count['inBees'],count['outBees'])

        #reset
        count['outBees']=0
        count['inBees']=0
        totalBees = [0]*8


# ---------------------------------------------------

# mqtt stuff ============================================
broker_address = "titi.etsii.urjc.es"
topic = "splendid/insert/counter"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"bc1")
client.on_connect = on_connect
client.connect(broker_address) 
client.loop_start() # Inicio del bucle

totalBees = [0]*8
# debug...
current = 1 # escape que puede pitar cuando cuente

# crea un buffer para cada escape (ys)
tam=2000
ys=[]
for i in range(8):
    ys.append([0]*tam) 

# cerrojo pra exclusion mutua
lock = threading.Lock()

# insertar en el servidor
threading.Thread(target=insertar).start()

# cada cierto tiempo cuenta los picos en los buffers
threading.Thread(target=contar,).start()

# leer valores de cada escape
leer()



