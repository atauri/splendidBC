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

# SETUP -----------------------------------------
# sensors are connected to rPi i2c, no serial, no esp...
CURRENT = 1
bufferSize = 1000 # Number of samples

count={
    "inEscapes":[1,0,0,1],
    "outEscapes":[0,1,1,0],
    "inBees":0,
    "outBees":0
}

# SOCKET =====================================================
soc = None # referneia al socket

class SimpleEcho(WebSocket):
    
    global soc ##


    def enviarDatos(self, l):
        #print("SEND ", l)
       
        self.send_message(json.dumps(l))
        
     

    '''Algo me llega por el socket - - - - - - - - - - - - - - - - - -'''
    def handle(self):
       print("algo llegó")

    #------------------------------------------------------
    def connected(self):
       
        global soc
        soc = self

        print(self.address, 'connectado a la interfaz')
        #hiloLeer = threading.Thread(target=self.enviarDatos)
        #hiloLeer.start()

    def handle_close(self):
        print(self.address, 'closed')
        terminar = False

# ============================================================

# 4 buffers, oner per escape
escapes = [[0]*bufferSize for _ in range(4)]


def findPeaks(serie):

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


def read():
    
    # connect
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)
    
    global count

    def drawPeaks(peaks):
        foundBees=[0]*bufferSize
        for p in peaks: foundBees[p]=1
        return foundBees

    i=0
    start_time = time.time()
    print(start_time)
    
    # read forever...
    while True:
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
            
            #print("\nin",count["inBees"],", out ",count["outBees"])
            
            #send to socket?
            print("SEND!!")
            peaks = findPeaks(escapes[CURRENT])
            soc.enviarDatos(
                {
                    "buffer1": escapes[CURRENT],
                    "buffer2": drawPeaks(peaks),
                    "bees": len(peaks)
                })

            i=0 #reset buffer
            start_time = time.time()
        i+=1         

# do the socket s s s s s s s s s s s s s s s s s s s s s s s s s s s s 
        
print("lanzar el soket")
def levantarSocket():
    # ARRANCAR WESOCKET ###
    print("levantar socket")
    server.serve_forever()

server = WebSocketServer('0.0.0.0', 9000, SimpleEcho)
hiloSc = threading.Thread(target=levantarSocket)
hiloSc.start()


# read data from sensors
print("leer")
read() 
       
