'''Apply find to samples stored in json files'''

import peaksLib
import glob
import json
import time

path = "/var/www/html/splendid/samples/"
path = "./samples/"
def iterateOverFiles():

    files = glob.glob(path+"*.json")
    
    for f in files: 
        print(f)
        file = open(f, 'r' )
        data = json.loads(file.read())
        file.close()

        
        for escape in range(4):
            #smoothed, peaks = peaksLib.findPeaks(data[escape]['mix'])
            #print(peaks)
            bees = procesarBuffers(data[escape]['interior'],data[escape]['exterior']) # devuelve lista con los picos dectectados
            peaksSerie = peaksLib.drawPeaks(bees, len(data[escape]['interior']))
            #print(peaksSerie)
            
            data[escape]['peaks'] = {
                "serie":peaksSerie,
                "peaks": len(bees),
                "smoothed":[]
            } 
            data[escape]['mix']=[]

        #print(data)    
        print("------------------------")

        file = open(f, 'w' )
        file.write(json.dumps(data))
        file.close()
        


# ====================================================

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
    print("l:",len(peaks)) # number of found peaks
    return(peaks)


def procesarBuffers(interior, exterior):

    print("Contar...")
    global totalBees

    t=time.time()


    inP=peaks(interior)
    exP=peaks(exterior)

    detectados = []
    for pico in inP:
        for x in exP:
            delta = pico-x
            #print(pico,",",x,":",delta)
            if abs(delta) < 30 :
                #print("OK!")
                #bees +=1
                if delta < 0:
                    #print("+1")
                    detectados.append(x)
                break

    print(detectados)
    return detectados
    #print("process time: "+str(time.time()-t),"\n\n")
    


iterateOverFiles()