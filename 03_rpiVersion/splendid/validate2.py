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
buzz.beep(1)

# SETUP -----------------------------------------

bufferSize = 5000 # Number of samples
totalBees = 0

# SOCKET =====================================================
soc = None # referne5a al socket
seguir = True

class SimpleEcho(WebSocket):
    
    global soc
    global totalBees

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
        print(self.address, 'el socket se ha cerrado')
 
        

# ============================================================


# read <size> samples
def read(size):

    # connect
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)
    cap.recalibrate()

    # 4 buffers, oner per escape
    escapes = [[0]*size for _ in range(4)]
    interior = [[0]*size for _ in range(4)]
    exterior = [[0]*size for _ in range(4)]
    buzz.beep(1)
    
    global totalBees
    global soc
   
    i=0
    start_time = time.time()

    # read 4 excapes {size} times...
    while i<size:
        try:
           for escape in range(4): #0..3
              
              x = cap[(escape*2)+1].raw_value/127.0 # 1,3,5,7
              y = cap[(escape*2)+2].raw_value/127.0 # 2,4,6,8
              if x<0:x=0
              if y<0: y=0
              interior[escape][i]=x
              exterior[escape][i]=y
              escapes[escape][i] = x*y
        
        except: pass
        i+=1

    # Buffers llenos, procesar:
    buzz.beep(1)    
    print("buffers llenos")

    for bf in range(4):
        try: 
            # Do it in all escapes to mimic real algotithm
            spline, bees = peaksLib.findPeaks(escapes[bf])
            msg={
                "escape": bf,
                "spline": spline,
                "interior": interior[bf],
                "exterior": exterior[bf],
                "peaks": peaksLib.drawPeaks(bees, size),
                "total": len(bees)
            }
            
            if soc: 
                soc.enviarDatos(msg)
        except Exception as e: 
            print(e)
            bees=[]

    # send buffers through socket
            
    '''if i>= buff
            
            end_time = time.time()
            # Calculate elapsed time
            elapsed_time = end_time - start_time
            print("\nElapsed time: ", elapsed_time)
            buzz.beep(1)
            # Count each buffer and acum data
            for bf in range(4):
                try: 
                    # Do it in all escapes to mimic real algotithm
                    bees = peaksLib.peaks(escapes[bf])
                except: 
                    bees=[]

            #send to socket?
            print("SEND escape ", str(CURRENT))
            print("totalBees", str(totalBees))
            suave, peaks = peaksLib.findPeaks(escapes[CURRENT])
            totalBees += len(peaks)
            
            msg={
                    "buffer1": suave.tolist(),
                    "buffer2": peaksLib.drawPeaks(peaks, bufferSize),
                    "bees": len(peaks),
                    "totalBees": str(totalBees)
                }
            #print(msg)
            if soc: soc.enviarDatos(msg)
            totalBees=0
            i=0 #reset buffer
            start_time = time.time()
            buzz.beep(1)'''
    i+=1         

def processEvent(e):
    print("event: ",e)


    if e=="kill":
        print("morir")
        #hiloSc.stop()

    # number of samples are comming
    else: read(int(e))
    

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
       
