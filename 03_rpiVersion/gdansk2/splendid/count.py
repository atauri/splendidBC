# IMPORTS
import time
import paho.mqtt.client as mqtt # use version 1.6.1 (see server version)
import threading
from getmac import get_mac_address as gma
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C
import peaksLib


# SETUP -----------------------------------------
# sensors are connected to rPi i2c

bufferSize = 6000 # Number of samples

totalEscapes = 4

count={
    "inEscapes":[0,1,0,1],
    "outEscapes":[1,0,1,0],
    "inBees":0,
    "outBees":0
}

# mqtt stuff
broker_address = "titi.etsii.urjc.es"
topic = "splendid/insert/counter"

## HARDWARE -------------------------------------------------
i2c = busio.I2C(board.SCL, board.SDA)

cap = CAP1188_I2C(i2c, 41) # default
cap.averaging = 4
cap.sample = "1.28ms"
cap.cycle = "35ms"

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


# read <size> samples =================================
def read(size, cap):

    print("Leer....")
    global totalBees

    #  1 buffer  per escape
    escapes = [[0]*size for _ in range(4)]
   
    # fill  buffers 
    i=0
    #start_time = time.time()
    
    print("GO!")
    # fill buffers
    while i<size:
        try:
            for escape in range(4): #0..3

              # Read CAP1188
              escapes[escape][i] = (127+cap.delta_count(escape+1))/255.0        
        except: pass
        i+=1

    print("buffers llenos")
    #print(str(time.time()-start_time))
    return escapes

# ====================================================

def procesarBuffers(escapes):

    print("Contar...")
    global count

    #t=time.time()

    for escape in  range(totalEscapes):

        bees, _ = peaksLib.countBeesMono(escapes[escape].copy())
                
        print("Escape ", escape," -> ", len(bees))
           
        # entran o salen?
        if count["inEscapes"][escape]==1: count['inBees'] += len(bees)
        if count["outEscapes"][escape]==1: count['outBees'] += len(bees)

    #print("process time: "+str(time.time()-t),"\n\n")
    print("\n", count);

# MQTT: let's go ===============================================

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"bc1")
client.on_connect = on_connect
client.connect(broker_address) 
client.loop_start() # Inicio del bucle

# cada x min un hilo vuelca los datos a mqtt
def ejecutar(espera=300):
    
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

while True:
    bf = read(bufferSize, cap)
    threading.Thread(target=procesarBuffers, args=(bf,)).start() 


