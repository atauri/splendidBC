import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
import threading

import socket
import sys
from struct import unpack

# Create figure for plotting
fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)
xs = [0]*2000
ys = [0]*2000
i=0

# Aquí leer por el socket del contador --------------
def soc():


    print("\nCrear Socket")

    global ys


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
            x  = unpack('f', message)
            #print(f'X: {x}')
            ys.append(x)
        except:pass
        #time.sleep(.01)

def animate(i):

    global ys

    try: 
        ys=ys[-2000:]
        ax.clear()
        ax.plot(ys, linewidth=1)

        # Format plot
        #plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('RT')
        plt.ylim(0,1)


    except: print("error")

    

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, interval=100)
hilo = threading.Thread(target=soc, name='hilo4').start()

plt.show()


