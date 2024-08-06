from datetime import datetime

import time
import threading
from scipy.signal import savgol_filter       
import socket

from struct import unpack

#para contar
# pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt # use version 1.6.1 (see server version)

import keyboard
import cv2
import json
import peaksLib

from beep import beep

# Teclado -----------------------------------------------------

# Resetear la gráfica
keyboard.add_hotkey('enter', lambda: reset())

totalEscapes = 4

count={
    "outEscapes":[0,1,0,1],
    "inEscapes":[1,0,1,0],
    "inBees":0,
    "outBees":0
}
'''
def on_connect(client, userdata, flags, rc):
    print("MQTT, on_connect")
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


def insertMqtt(inBees, outBees, 
               mac="00:00:00:00:00:01",
               timeZone="Europe/Madrid", 
               myMac="00:00:00:00:00:01"):

    payload = "{"+'"mac":"{}","inBees": {},"outBees": {},"timeZone":"{}","user": "{}"' \
        .format(mac,inBees, outBees, timeZone, myMac ) +"}"

    print(payload)
    result = client.publish(topic, payload)
    print("Result: ", result)
    return
'''
#======================================================


def beeps(n=1):

    for _ in range(n):
        frequency = 840
        duration = 100
        beep(frequency, duration) # duration in ms, frequency in Hz
        time.sleep(.2)
        

# Aquí leer por el socket del contador --------------
def reset():

    global ys
    global total
    global totalBees
    global lastFound

    ys = [0]*tam 
    total = []
    totalBees = 0
    lastFound = 0


def soc(  ):

    print("\nCrear Socket")

    global ys
    global lock
    global total # Array con todas las muestras
    global totaBees

    # crear el socket (servidor)
    # Tengo que saber mi IP (y ponérsela fija en e el router)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    host, port = '0.0.0.0', 65000
    server_address = (host, port)

    print(f'Starting UDP server on {host} port {port}, esperando cliente')
    sock.bind(server_address)

    # Recibo las muestras
    while True:
        # Wait for message
        message, _ = sock.recvfrom(4096)

        #los añado por una punta y los quito por la otra
        try: 
            x  = unpack('8f', message)
            lock.acquire()
            for i in range(8): #itera en cada escape
                ys[i].append(x[i])
                ys[i].pop(0)
            lock.release()

        except Exception as e : print(e)
    

def contar():
    global current
    global ys
    global lock
    totalBees = [0]*8
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
                if pitar: beeps(inc)
            last = nBees

        except Exception as e: print("Error:",e)
        
        return total, last
    
    
    while True:

        time.sleep(1)
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
        print(totalBees)
        
    
# ---------------------------------------------------

beeps(3)

# mqtt stuff ============================================
'''broker_address = "titi.etsii.urjc.es"
topic = "splendid/insert/counter"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"bc1")
client.on_connect = on_connect
client.connect(broker_address) 
client.loop_start() # Inicio del bucle'''



current = 0 # escape que puede pitar cuando cuente

# crea un buffer para cada escape (ys)
tam=2000
ys=[]
for i in range(8):
    ys.append([0]*tam) 

# cerrojo pra exclusion mutua
lock = threading.Lock()

#ani = animation.FuncAnimation(fig, animate, interval=250)

# lee de socket indefinidamente
data = threading.Thread(target=soc,).start()

# cada cierto tiempo cuenta los picos en los buffers
threading.Thread(target=contar,).start()

#plt.show()




