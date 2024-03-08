import cv2
from datetime import datetime
import json
import threading
import time
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C

# function video capture

'''Beecounter class'''
class BC():
    position = 0
    
    def __init__(self, size):

        i2c = busio.I2C(board.SCL, board.SDA)
        self.cap = CAP1188_I2C(i2c)

        self.bufferSize = size
        self.buffer1=[0]*size # electrodo interior
        self.buffer2=[0]*size # electtrodo exterior
        #self.i=0 # buffer index


    def readEscape(self, escape):
        
        print("read {} samples".format(self.bufferSize))

        for i in range(self.bufferSize):

            x = self.cap[(escape*2)+1].raw_value/127.0 # 1,3,5,7
            y = self.cap[(escape*2)+2].raw_value/127.0 # 2,4,6,8
            if x<0:x=0
            if y<0: y=0
            #print(i, x, y)
            self.buffer1[i] = x
            self.buffer2[i] = y
            self.position=i

def setupVideo(nombre):

    cameraCapture = cv2.VideoCapture(-1)
    # rame rate or frames per second
    fps = 15
    # Width and height of the frames in the video stream
    size = (int(cameraCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cameraCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    videoWriter = cv2.VideoWriter(nombre+'.mp4', 
    cv2.VideoWriter_fourcc('D','I','V','X'), fps, size) # este funciona bien en la pi zero 2w
    print("writer ok")
    return cameraCapture, videoWriter

 
'''success, frame = cameraCapture.read()
 
# some variable
numFramesRemaining = 5*fps - 1
 
# loop until there are no more frames and variable > 0
while success and numFramesRemaining > 0:
    print(numFramesRemaining)
    videoWriter.write(frame)
    success, frame = cameraCapture.read()
    #cv2.imshow('frame',frame)
    cv2.waitKey(1)
    numFramesRemaining -= 1
 
#Closes video file or capturing device
cameraCapture.release()
'''

def leerDatos(bc):

    
    bc.readEscape(1)
    print("Parar")

def grabarVideo(video, writer):

    font = cv2.FONT_HERSHEY_SIMPLEX
   
    #leer de los sensores
    bc = BC(5000)
    hilo = threading.Thread(target = leerDatos, args=([bc]))
    hilo.start()

    print("go with the video")
    while (bc.position==0):
        print("z")
        time.sleep(.1)
    while (bc.position<999):

        #success, frame = video.read()
        #writer.write(frame)
        print(bc.position)

    video.release()

    # esperar a que el sensor sute la basura


    return
    
#===============================
# video filename
now = datetime.now() 
nombre = now.strftime("%Y_%m_%d__%H_%M_%S")
print("------------------------------------\ndate and time:",nombre)	

v, w = setupVideo(nombre)
grabarVideo(v,w) # sincronos

print("fin de la app")

'''if len(splendidBC.buffer)>=splendidBC.tamBuffer:
    splendidBC.patronaje.guardarBuffer(splendidBC.buffer, splendidBC.buffer2, nombre)
'''
   
