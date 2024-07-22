#!/usr/bin/env python3

import socket
import sys
from time import sleep
import random
from struct import pack
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C

current = 2

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IP DEL SERVIDOR DEL SOCKE (ej Mac mini, o pc)
host, port = '192.168.1.239', 65000 # macmini - splendid
server_address = (host, port)



# Recibe el socket
def read(sc):
    

    # connect
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)

    cap.averaging = 4 #averages = (1, 2, 4, 8, 16, 32, 64, 128)
    cap.sample="640us" #("320us", "640us", "1.28ms", "2.56ms")
    cap.cycle="35ms" # "35ms", "70ms", "105ms", "140ms"
     
    print(f"Sensor Initial Configuration Values: {cap.averaging, cap.sample, cap.cycle}")
   
    # 4 buffers, oner per escape
    escapes = [0]* 4 #nu,ero de escapes (4 u 8)
           

    #buzz.beep(1)

    while True:

        # Hacer un barrido
        try:
           for escape in range(4): #0..3
               escapes[escape] = (127+cap.delta_count(escape+1))/255.0
                  
        except Exception as e: print(e)
        

        # Enviar por socket UN escape
        #print(type(escapes[current]))
        msg = pack('f', escapes[current]) 
        sc.sendto(msg, server_address)


#============================
read(sock)

   
