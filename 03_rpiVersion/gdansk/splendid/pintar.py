import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
import threading

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = [0]*2000
ys = [0]*2000

i=0

# Aquí leer por el socket del contador --------------
def soc():
    global xs
    global ys
    global i

    while True:
        temp_c = i #random.randint(3, 9)/10
        i+=1

        if i==100: i = 0

        ys.append(temp_c)

        time.sleep(.01)

def animate(i):

    global xs
    global ys
    '''# Read temperature (Celsius) from TMP102
    temp_c = random.randint(3, 9)/10 

    # Add x and y to lists
    xs.append(len(ys)+1)
    ys.append(temp_c)
'''
    
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


