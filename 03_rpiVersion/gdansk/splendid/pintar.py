from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
import threading
from scipy.signal import savgol_filter       
import socket
import sys
from struct import unpack

#from webcam import Webcam
import keyboard
import cv2
import json

# teclado

# Cambiar el escape
keyboard.add_hotkey('1', lambda: ipo(0))
keyboard.add_hotkey('2', lambda: ipo(1))
keyboard.add_hotkey('3', lambda: ipo(2))
keyboard.add_hotkey('4', lambda: ipo(3))
keyboard.add_hotkey('5', lambda: ipo(4))
keyboard.add_hotkey('6', lambda: ipo(5))
keyboard.add_hotkey('7', lambda: ipo(6))
keyboard.add_hotkey('8', lambda: ipo(7))

# Resetear la gráfica
keyboard.add_hotkey('enter', lambda: reset())

# parar y contar
parar = threading.Event()
grabando = threading.Event()

keyboard.add_hotkey('c', lambda: grabarVideo(parar, grabando))

# Grabar un video
def grabarVideo(detener, grabar):

    video = threading.Thread(target=getVideo, args=(detener, grabar)).start()
   
    
def detenerVideo(ev):
    print("terminar dentro de 30 sg")
    time.sleep(30)
    ev.set()


# Aquí leer por el socket del contador --------------
def reset():

    global ys
    global total

    ys = [0]*tam 
    total = []


# selecciona el escape
def ipo( escp):

    global currentEscape
    currentEscape= escp



def soc( grabando ):

    print("\nCrear Socket")

    global ys
    global lock
    global total

    # crear el socket (servidor)
    # Tengo que saber mi IP (y ponérsela fija en e el router)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    host, port = '0.0.0.0', 65000
    server_address = (host, port)

    print(f'Starting UDP server on {host} port {port}, esperando cliente')
    sock.bind(server_address)

    # Recibo las muestras
    while True:
        # Wait for message
        message, _ = sock.recvfrom(4096)

        #print(f'Received {len(message)} bytes:')
        try: 
            x  = unpack('8f', message)
            
            lock.acquire()
            ys.append(x[currentEscape])
            ys.pop(0)
            lock.release()
            if grabando.is_set():  total.append(x[currentEscape])  

        except Exception as e : print(e)
    

def animate(i):

    global ys
    global lock

    ax.clear()
    lock.acquire()
    y = ys.copy()
    try:  
        suave = savgol_filter(y, window_length=20, polyorder=2) 

    except Exception as e: print("SUAVIZAR:",e)
    try:        
        ax.plot(suave, color="black", linewidth=.75)
    except Exception as e: print("PINTAR:", e)
    lock.release()
    
    plt.subplots_adjust(bottom=0.10, left=0.10)
    plt.title('Splendid escape '+str(currentEscape))
    plt.ylim(0,1)
    

def getVideo(para, graba):

    nombreFichero = datetime.today().strftime('%Y-%m-%d_%H.%M')
    print(" grabar video :", nombreFichero)

    vid = cv2.VideoCapture(1) 
    frame_width = int(vid.get(3)) 
    frame_height = int(vid.get(4)) 
    size = (frame_width, frame_height) 

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    result = cv2.VideoWriter(f'./videos/{nombreFichero}.mp4',  
            fourcc, 
            25, size) 

    reset()
    # indica al sensor que comience a guardar los datos en el array total
    graba.set()

    # Para a los x segundos si no se sale con 'q'
    threading.Thread(target=detenerVideo, args=(para,)).start()
    while(True): 
      
        # Capture the video frame 
        ret, frame = vid.read() 
        result.write(frame) 
        # Display the resulting frame 
        cv2.imshow('frame', frame) 
        
        # the 'q' button is set as the 
        # quitting button you may use any 
        # desired button of your choice 
        if cv2.waitKey(1) & 0xFF == ord('q'): break
        if para.is_set(): 
            print("Parada programada")
            break
            
    # notificar a otros hilos        
    para.clear()
    grabando.clear()        

    # liberar la camara
    vid.release() 
    result.release()

    # grabar los datos del sensor
    print("Datos grabados:", len(total))
    with open(f'./videos/{nombreFichero}.json', 'w') as f:
        json.dump({'bees':False,'sensor':total}, f)
    cv2.destroyAllWindows()     
    
    print("fin")
    

# ---------------------------------------------------



currentEscape = 5

# Create figure for plotting
fig = plt.figure()
fig.set_figwidth(200)
ax = fig.add_subplot(1, 1, 1)

tam=2000
ys = [0]*tam 


lock = threading.Lock()

ani = animation.FuncAnimation(fig, animate, interval=250)
data = threading.Thread(target=soc, args=(grabando,)).start()
#video = threading.Thread(target=getVideo).start()

plt.show()




