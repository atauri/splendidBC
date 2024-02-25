# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

import serial # pip install pyserial
import time


# SETUP -----------------------------------------
mac= "/dev/tty.usbserial-0001" # mac port
win = "COM19" # win port
rpiPort = "---"
what = mac # Connectig to who (mac, win or rpi)
bufferSize = 1000 # Number of samples

# 4 buffers, oner per escape
escapes = [[0]*bufferSize for _ in range(4)]

def peaks(serie):

    from scipy.signal import find_peaks
    import numpy as np

    # remove noise applying savgol filter
    def suavizar(serie):
        from scipy.signal import savgol_filter
        suave = savgol_filter(serie, window_length=50, polyorder=2)
        return suave
    
    #suave =  suavizar(serie)
    #print(serie)
    peaks, _ = find_peaks(serie, height=.25, prominence=.2, distance=50)
    #print(peaks)
    #print(len(peaks)) # number of found peaks
    return(peaks)

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

    i=0
    start_time = time.time()
    print(start_time)
    while True:
        try:
            # read from esp
            # electrodes came already multiplied and normalizad 0..1
            line = str(pserie.readline().strip())[2:-2].split(",")
            
            for bf in range(4):
                #print(line[bf],)
                escapes[bf][i] = line[bf]
        except: pass
        
        # Whe buffer is full counte all the escapes    
        if i>= bufferSize:
            end_time = time.time()
            # Calculate elapsed time
            elapsed_time = end_time - start_time
            print("\nElapsed time: ", elapsed_time)
            
            #Count each buffer
            for bf in range(4):
                
                try: bees = peaks(escapes[bf])
                except: 
                    bees=""
                print(str(bf),":",len(bees))
            i=0 #reset buffer
            start_time = time.time()
        i+=1         

pserie=conectar()
read(pserie)