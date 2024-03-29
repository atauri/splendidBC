# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

'''
reads data from sensor,
and send to UI by socket
'''

import time
import threading
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C
from simple_websocket_server import WebSocketServer, WebSocket
import json
import sys
from events import Events
import peaksLib

# SETUP -----------------------------------------
# sensors are connected to rPi i2c, no serial, no esp...
CURRENT = 1
bufferSize = 1000 # Number of samples

totalBees = 0

# SOCKET =====================================================
soc = None # referne5a al socket
seguir = True

class SimpleEcho(WebSocket):
    
    global soc ##
    global CURRENT
    global totalBees

    def enviarDatos(self, l):
        #print("SEND ", l)
        try: self.send_message(json.dumps(l))
        except: print("no estoy connected")

    '''Algo me llega por el socket - - - - - - - - - - - - - - - - - -'''
    def handle(self):

       print("algo llegó: ",self.data )

       if self.data=="x":
            print("BYE")
            soc.close()
            events.on_change("kill")            
       
       global CURRENT
       global totalBees

       CURRENT = int(self.data)
       totalBees = 0
       events.on_change("resetBuffer")  

    #------------------------------------------------------
    def connected(self):
       
        global soc
        soc = self

        print(self.address, 'connectado a la interfaz')
        #hiloLeer = threading.Thread(target=self.enviarDatos)
        #hiloLeer.start()

    def handle_close(self):
        print(self.address, 'cerrar y morir')
        #server.close()
     
        

# ============================================================

# 4 buffers, oner per escape
escapes = [[0]*bufferSize for _ in range(4)]

def read():

    # connect
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)
    
    global totalBees

    i=0
    start_time = time.time()
    
    # read forever...
    while seguir:
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

            i=0 #reset buffer
            start_time = time.time()
        i+=1         

def processEvent(e):
    print("event: ",e)
    global seguir

    if e=="kill":
        seguir = False
        hiloSc.stop()

    if e=="resetBuffer":
        escapes[CURRENT] = [0]* bufferSize
        print("reseteado")
    #sys.exit(0)

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
print("leer")
read() 
       
