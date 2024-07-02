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

bufferSize = 4000 # Number of samples
doble= False

totalEscapes = 4
if doble: totalEscapes = 8

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

cap2 = None
if doble: 
    cap2 = CAP1188_I2C(i2c, 40) # wire in cap1188 adc-->Vin
    cap2.averaging = 4
    cap2.sample = "2.56ms"
    cap2.cycle = "140ms"

cap1 = CAP1188_I2C(i2c, 41) # default
cap1.averaging = 4
cap1.sample = "2.56ms"
cap1.cycle = "140ms"


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
    print("Result: ", result)
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
              if doble:
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

def procesarBuffers(interior, exterior):

    print("Contar...")
    global count

    t=time.time()

    for escape in  range(totalEscapes):

        bees, _, _, _, _ = peaksLib.countBees(interior[escape], exterior[escape])
                
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
    i,e = read(bufferSize, cap1, cap2)
    threading.Thread(target=procesarBuffers, args=(i,e)).start() 


