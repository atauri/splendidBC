import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
import threading
from scipy.signal import savgol_filter
        
import socket
import sys
from struct import unpack

import keyboard
keyboard.add_hotkey('space', lambda: ipo())

currentEscape = 5
#from webcam import Webcam

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
 
ys = [0]*2000 

# Aquí leer por el socket del contador --------------
def ipo():
    global currentEscape

    currentEscape+=1
    if currentEscape == 8: currentEscape = 0

def soc():

    print("\nCrear Socket")

    global ys
    global lock

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
        except Exception as e : print(e)
        #time.sleep(.01)
    

def animate(i):

    global ys
    global lock

    ax.clear()
    lock.acquire()
    y = ys.copy()
    try:  
        suave = savgol_filter(y, window_length=50, polyorder=1) 

    except Exception as e: print("SUAVIZAR:",e)
    try:        
        ax.plot(suave, color="black", linewidth=.75)
    except Exception as e: print("PINTAR:", e)
    lock.release()
    
    plt.subplots_adjust(bottom=0.30)
    plt.title('Splendid escape '+str(currentEscape))
    plt.ylim(0,1)
    
'''def getVideo():
    
    import cv2
    capture = cv2.VideoCapture(1)
 
    while (capture.isOpened()):
        ret, frame = capture.read()
        cv2.imshow('webCam',frame)
        if (cv2.waitKey(1) == ord('s')):
            break
    
    capture.release()
    cv2.destroyAllWindows()'''


lock = threading.Lock()

ani = animation.FuncAnimation(fig, animate, interval=250)
data = threading.Thread(target=soc).start()
#video = threading.Thread(target=getVideo).start()


#currentEscape = int(input("Escape?"))
#
plt.show()

print("??")


