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

    ''' PARA EL CLIENTE
    #!/usr/bin/env python3

    import socket
    import sys
    from time import sleep
    import random
    from struct import pack

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    host, port = '192.168.0.8', 65000
    server_address = (host, port)

    # Generate some random start values
    x, y, z = random.random(), random.random(), random.random()

    # Send a few messages
    for i in range(10):

        # Pack three 32-bit floats into message and send
        message = pack('3f', x, y, z)
        sock.sendto(message, server_address)

        sleep(1)
        x += 1
        y += 1
        z += 1
    '''

    print("\nCrear Socket")
    global xs
    global ys
    global i

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
        message, address = sock.recvfrom(4096)

        #print(f'Received {len(message)} bytes:')
        x  = unpack('f', message)
        #print(f'X: {x}')

        # añadir la lectura al grafico ....
        temp_c = x #random.randint(3, 9)/10
        ys.append(temp_c)
        #time.sleep(.01)

def animate(i):

    global ys
    global xs

    # Limit x and y lists to 20 items
    xs=xs[-200:]
    ys=ys[-200:]
    ax.clear()
    
    ax.plot(ys)

    # Format plot
    #plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('RT')
    plt.ylabel('Temperature (deg C)')




# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, interval=100)
hilo = threading.Thread(target=soc, name='hilo4').start()

plt.show()


