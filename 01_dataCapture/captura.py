'''Caputar un video y el bufer del sensor y guardarlo el disco
para poseriormente sacar ventanas, prediciones y patronens de entrnamiento
mejor que hacer en tiempo real'''

''' A 3fps y el sensor delay(2) salen 66 valores de capacidad por frame'''
import cv2
import time
import threading
import splendidBC
from bottle import route, run, template
from datetime import datetime
import json

## video ---------------------------------------------------------------------------------------
def setupVideo(nombre):
    video = cv2.VideoCapture(0)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    writer = cv2.VideoWriter('./capturas/'+nombre+'.mp4', cv2.VideoWriter_fourcc(*'H264'), fps, (width,height))
    #writer = cv2.VideoWriter('./capturas/'+nombre+'.mp4', cv2.VideoWriter_fourcc(*'divx'), fps, (width,height))
    print("writer ok")
    return video, writer

def grabarVideo(video, writer):
    font = cv2.FONT_HERSHEY_SIMPLEX
   
    '''leer de los sensores'''
    hilo = threading.Thread(target=splendidBC.get, args=())
    hilo.start()
    
     ## esperar a que el sensor sute la basura
    while splendidBC.esperandoDatos:
        print("z")
        time.sleep(1)
    
    # lee hasta que se llene el buffer
    ret,frame= video.read()
    splendidBC.buffer=[]
    splendidBC.buffer2=[]
    
    splendidBC.i=0
    start = time.time()
    t=[]
    i=0
    
    print("empezar")
    while splendidBC.leyendo:
        
        n=splendidBC.i
        #if n%5==0:
        ret,frame= video.read()
        end = time.time()
        t.append(n)
        i+=1
        cv2.putText(frame, " {:0.2f}s: {}".format((end - start),n),
            (5,100), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
        writer.write(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
    # guardar sicronizacion            
    if len(splendidBC.buffer)>=splendidBC.tamBuffer:
        with open('./capturas/'+nombre+'.t_json', 'w') as f:
            f.write(json.dumps(t))
        

    # ha terminado
    video.release()
    writer.release()
    cv2.destroyAllWindows() 

# ===========================


now = datetime.now() 
nombre = now.strftime("%Y_%m_%d__%H_%M_%S")
print("------------------------------------\ndate and time:",nombre)	


v, w = setupVideo(nombre)
grabarVideo(v,w) # sincronos

print("fin")
if len(splendidBC.buffer)>=splendidBC.tamBuffer:
    splendidBC.patronaje.guardarBuffer(splendidBC.buffer, splendidBC.buffer2, nombre)

   