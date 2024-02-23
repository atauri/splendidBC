# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

import serial # pip install pyserial
import time
import matplotlib.pyplot as plt

# SETUP -----------------------------------------
mac= "/dev/tty.usbserial-0001" # mac port
win = "COM19" # win port
rpiPort = "---"
what = mac # Connectig to who (mac, win or rpi)
bufferSize = 1000 # Number of samples

escape=1 # which funnel to process...


def peaks(interior, exterior):

    from scipy.signal import find_peaks
    import numpy as np

    # remove noise applying savgol filter
    def suavizar(serie):
        from scipy.signal import savgol_filter
        #suave = savgol_filter(serie, window_length=100, polyorder=2) /127
        suave = savgol_filter(serie, window_length=50, polyorder=2)
        return suave
    
    # multiply both electrodes (in rage 0..1)
    combi=[]
    for i in range(len(exterior)):
        combi.append(exterior[i]*interior[i])

    combi =  suavizar(combi)
    peaks, _ = find_peaks(combi, height=.25, prominence=.2, distance=100)
    
    print(peaks)
    picos = [0]*len(combi)
    for p in peaks: picos[p]=1

    print(len(peaks)) # number of found peaks
    return(combi, picos)

    r={
        "bees": combi.tolist(), # this will be area chart
        "totalBees": len(peaks)
    }
    



'''Connect serial port'''
def conectar():
    con = False
    while not con:
        try:
            ser = serial.Serial(port=what,  baudrate=115200)
            con = ser.isOpen()
            print("ESP connected :-))")
        except Exception as e:
            print(e)
            time.sleep(1)
    return ser

def read(pserie):

    interior = [0]*bufferSize
    exterior = [0]*bufferSize
    i=0
    while True:
        line = str(pserie.readline().strip())[2:-2].split(",")
        #print(line)
        try:
            x = int(line[escape*2])
            y = int(line[escape*2+1])
            interior[i]= x/127
            exterior[i]= y/127

            i+=1
            #print(val)
            if i>= bufferSize:
                i=0
                ax.clear()  # erase the chart
                ax.plot(interior)
                ax.plot(exterior)
                serie, picos = peaks(interior, exterior)
                ax.plot(serie) 
                ax.plot(picos, color="r")
                plt.draw()
                plt.pause(0.05)
        except: pass

# CREATE A MATPLOT CHART 
fig = plt.figure()  
ax = fig.add_subplot()

pserie=conectar()
read(pserie)