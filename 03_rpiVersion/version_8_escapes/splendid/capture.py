import os
import time
from datetime import datetime
import threading
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C
import json
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

picam2 = Picamera2()
config = picam2.create_preview_configuration()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

encoder = H264Encoder(10000000)

bufferSize = 5000 # 5000 -> aprox 30sg


escapes = [ {
    'bees': False, # edit later counting in the video
    'interior':[0]*bufferSize,
    'exterior':[0]*bufferSize,
    'mix': [0]*bufferSize
    } for _ in range(4)]

def getName():
    now = datetime.now() 
    nombre = now.strftime("/home/tadu/samples/%Y_%m_%d__%H_%M_%S")
    print("------------------------------------\ndate and time:",nombre)
    return(nombre)

def read():

    i2c = busio.I2C(board.SCL, board.SDA)
    cap = CAP1188_I2C(i2c)
    
    cap.averaging = 4
    cap.sample = "1.28ms" #Sensibilty
    cap.cycle = "35ms"

    i=0
    start_time = time.time()
    print("empezar")
    picam2.start()

    nombre = getName()
    picam2.start_recording(encoder, nombre+'.h264')

    while True:
        # read from esp
        # electrodes came already multiplied and normalizad 0..1

        try:
           for escape in range(4): #0..3

              x = (127+cap.delta_count((escape*2)+1))/255.0 # 1,3,5,7
              y = (127+cap.delta_count((escape*2)+2))/255.0
              
              escapes[escape]['interior'][i] = x
              escapes[escape]['exterior'][i] = y
              escapes[escape]['mix'][i] = x*y

        except Exception as e: print(e)

        # Whe buffer is full save data to file
        if i == bufferSize:

            end_time = time.time()
            # Calculate elapsed time
            elapsed_time = end_time - start_time
            print("\nElapsed time: ", elapsed_time)
            
            # Count each buffer and acum data
            '''for bf in range(4):
                try:
                    print(bf)
                    #bees = peaks(escapes[bf])
                except:
                    pass
                    #bees=[]
            '''
            picam2.stop_recording()
            js = json.dumps(escapes)
            
            f = open(nombre+".json", "w")
            f.write(js)
            f.close()

            # esperar o hacer otras cosas (convertir video...)
            #command = "ffmpeg -i {}.h264 {}.mp4".format(nombre, nombre)
            # borrar h264
            #print(command)
            #os.system(command)
            # borrar viejo
            #os.system("rm "+nombre+".h264")
            # enviar a titi
            command ="scp -r -P 222  /home/tadu/samples/ tadu@titi.etsii.urjc.es:/var/www/html/splendid/"
            os.system(command)
            # borrar viejo
            os.system("rm -rf ~/samples/*")
            
            # New sample
            nombre = getName()
            picam2.start_recording(encoder, nombre+'.h264')
            start_time = time.time()
            i=0 #reset buffer
            #new loop
        i+=1

read()


