
'''
reads data from sensor,
count peaks for 4 escapes
then insert in the server in MQTT
'''
# IMPORTS
import time
import paho.mqtt.client as mqtt # use version 1.6.1 (see server version)
import threading
from getmac import get_mac_address as gma
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C


# SETUP -----------------------------------------
# sensors are connected to rPi i2c

bufferSize = 1000 # Number of samples
totalEscapes = 8

count={
    "inEscapes":[0,1,0,1],
    "outEscapes":[1,0,1,0],
    "inBees":0,
    "outBees":0
}

# mqtt stuff
broker_address = "titi.etsii.urjc.es"
topic = "splendid/insert/counter"

## HARDWARE
i2c = busio.I2C(board.SCL, board.SDA)
cap1 = CAP1188_I2C(i2c, 40) # wire in cap1188 adc-->Vin
cap2 = CAP1188_I2C(i2c, 41) # default

totalBees = 0


def on_connect(client, userdata, flags, rc):
    print("MQTT, on_connect")
    if rc==0:
        print("connected OK Returned code=",rc)
    else:
        print("Bad connection Returned code=",rc)


def insertMqtt(inBees, outBees, mac="00:00:00:00:00:01",timeZone="Europe/Madrid", myMac="00:00:00:00:00:01"):
    payload = "{"+'"mac":"{}","inBees": {},"outBees": {},"timeZone":"{}","user": "{}"' \
        .format(mac,inBees, outBees, timeZone, myMac ) +"}"

    print(payload)
    result = client.publish(topic, payload)
    print(result)
    return


# read <size> samples =================================
def read(size, c1, c2):
    print("Leer....")
    global totalBees

    #8 buffers interior + 8 exterior, 1 per escape
    interior = [[0]*size for _ in range(totalEscapes)]
    exterior = [[0]*size for _ in range(totalEscapes)]

    # fill  buffers 
    i=0
    start_time = time.time()
    print("GO!")
    while i<size:
        try:
            for escape in range(4): #0..3

              # First CAP1188
              x = c1[(escape*2)+1].raw_value/127.0 # 1,3,5,7
              y = c1[(escape*2)+2].raw_value/127.0 # 2,4,6,8
              if x<0:x=0
              if y<0: y=0
              interior[escape][i]=x
              exterior[escape][i]=y

              # SECOND CAP1188
              x = c2[(escape*2)+1].raw_value/127.0 # 1,3,5,7
              y = c2[(escape*2)+2].raw_value/127.0 # 2,4,6,8
              
              if y<0: y=0
              interior[escape+4][i]=x
              exterior[escape+4][i]=y
        except: pass
        i+=1

    print("buffers llenos")
    print(str(time.time()-start_time))
    return interior, exterior

# ====================================================

def peaks(serie):

    from scipy.signal import find_peaks
    import numpy as np

    # remove noise applying savgol filter
    def suavizar(serie):
        from scipy.signal import savgol_filter
        suave = savgol_filter(serie, window_length=50, polyorder=2)
        return suave

    suave =  suavizar(serie)
    #print(serie)
    peaks, _ = find_peaks(serie, height=.25, prominence=.2, distance=50)
    #print(peaks)
    #print(len(peaks)) # number of found peaks
    return(peaks)



def procesarBuffers(interior, exterior):
    print("Contar...")
    global totalBees

    t=time.time()

    for escape in  range(totalEscapes):

        inP=peaks(interior[escape])
        exP=peaks(exterior[escape])

        #print(inP)
        #print(exP)
        bees=0
        for pico in inP:
            for x in exP:
                delta = pico-x
                #print(pico,",",x,":",delta)
                if abs(delta) < 100 :
                    #print("OK!")
                    #bees +=1
                    #if delta < 0:
                        #print("+1")
                    bees+=1
                    break

        print("Escape ", escape," -> ", bees)
        #totalBees+=bees
        # entran o salen?
        if count["inEscapes"]==1: count['inBees'] += bees
        if count["outEscapes"]==1: count['outBees'] += bees
        

    print("process time: "+str(time.time()-t),"\n\n")
    print("\nTotalbees: ", totalBees);

# MQTT: let's go ===============================================

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"bc3")
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

print("My Mac: ",gma())


# lanza el hilo que inserta en MQTT
insertThread = threading.Thread(target=ejecutar, kwargs={'espera': 300,}).start()

# Leer for ever
# for x in range (5):
while True:
    i,e = read(bufferSize, cap1, cap2)
    threading.Thread(target=procesarBuffers, args=(i,e)).start() 

