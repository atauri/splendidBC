# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

'''
reads data from sensor,
and send it to UI by socket
'''

import time
import threading
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C
from simple_websocket_server import WebSocketServer, WebSocket
import json
from events import Events
import peaksLib
import buzz

# SETUP -----------------------------------------

bufferSize = 6000 # Number of samples
totalBees = 0
buffer2send = False

stop = True

# SOCKET =====================================================
soc = None # referne5a al socket
seguir = True

class SimpleEcho(WebSocket):
    
    global soc
    global totalBees
    global stop


    def enviarDatos(self, l):
        print("SEND ")
        try: 
            
            self.send_message(json.dumps(l))
        except Exception as e: 
            print(e)

    '''Algo me llega por el socket - - - - - - - - - - - - - - - - - -'''
    def handle(self):

       print("algo llegó: ",self.data )

       if self.data=="x":
            print("BYE")
            events.on_change("kill")            
       else:
           print(self.data) 
           events.on_change(self.data)

    #------------------------------------------------------
    def connected(self):
       
        global soc
        soc = self
        print(self.address, 'connectado a la interfaz')
       

    def handle_close(self):
        
        global buffer2send
        print(self.address, 'el socket se ha cerrado')
        buffer2send = True
        

# ============================================================


# read <size> samples
def read(size, bf2send):
    
    #if not bf2send:
    #    print("no escapes selected")
    #    return

    # connect
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)
    #cap.recalibrate()

    cap.averaging = 4 #averages = (1, 2, 4, 8, 16, 32, 64, 128)
    cap.sample="1.28ms" #("320us", "640us", "1.28ms", "2.56ms")
    cap.cycle="35ms" # "35ms", "70ms", "105ms", "140ms"
    print("bf2send: ",str(bf2send)) 
    print(f"Sensor Initial Configuration Values: {cap.averaging, cap.sample, cap.cycle}")
    # 4 buffers, oner per escape
    escapes = [[0]*size for _ in range(4)]
           
    global totalBees
    global soc
      
    i=0
    start_time = time.time()

    # read 4 excapes {size} times...
    buzz.beep(1)
    while i<size:
        try:
           for escape in range(4): #0..3
               escapes[escape][i] = (127+cap.delta_count(escape+1))/255.0
                  
        except Exception as e: print(e)
        i+=1

    # Buffers llenos, procesar:
    buzz.beep(1)
    print("buffers llenos")

    for bf in range(4):
        try: 
            # Do it in all escapes to mimic real algotithm
            peaks, suave = peaksLib.countBeesMono(escapes[bf].copy())
            msg={
                
                #"spline": spline,
                "interior": suave, ##interior[bf],
                "exterior": escapes[bf], ##exterior[bf],
                "intPeaks": [], #peaksLib.drawPeaks(peaks, size, .25),
                "extPeaks": [], #peaksLib.drawPeaks(extPeaks, size, .25),
                "peaks": peaksLib.drawPeaks(peaks, size, 1),# marcas verticales
                "total": len(peaks)
            }
            
            if soc and bf == bf2send: 
                print("buffer:"+ str(bf)+" t:"+str(time.time()-start_time))
                soc.enviarDatos(msg)
        except Exception as e: 
            print(e)
            peaks=[]

    i+=1         

def doBucle(b):

    global buffer2send
    global stop
    print("doBucle, escape: ",b)
    #while not stop:
    #    print("leer buffer: ",b, bufferSize)
    read(bufferSize, b-1)
    
    print("he terminado")

def processEvent(e):

    global buffer2send
    global stop

    print("event: ",e)
    if e=="kill":
        print("parar")
        stop = True

    # numberof escape
    else:
        stop = False
        buffer2send = int(e)+1
        threading.Thread(target=doBucle, args=(buffer2send,)).start()


# do the socket s s s s s s s s s s s s s s s s s s s s s s s s s s s s 
        
print("lanzar el soket")
def levantarSocket():
    # ARRANCAR WESOCKET ###
    print("levantar socket")
    server.serve_forever()

events = Events()
events.on_change += processEvent

server = WebSocketServer('0.0.0.0', 9000, SimpleEcho)

hiloSc = threading.Thread(target=levantarSocket)
hiloSc.start()


# read data from sensors
#print("leer")
#read() 
       
