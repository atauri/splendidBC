from scipy.signal import find_peaks
import numpy as np

# Setup ----
# smooth curve
witdh = 100
order = 1

# peak detection
peakHeight = .2
prominence = .15
peakWitdh = 25

maxDelta = 100 # Distancia max entre 2 picos interior y exterior

def findPeaks(serie):

    # remove noise applying savgol filter
    def suavizar(serie):

        from scipy.signal import savgol_filter
        suave = savgol_filter(serie, window_length=witdh, polyorder=order)
        return suave
    
    suave = suavizar(serie)
    
    # devuelve una lista con las x donde hay picos
    peaks, _ = find_peaks(suave, height=peakHeight, prominence=prominence, distance=peakWitdh)
    
    # Devolver la curva suavizada y la lista de picos
    return(suave.tolist(), peaks.tolist())

'''un array de 0's tan largo como la serie original  con un 1  en cada pico'''
def drawPeaks(peaks, bufferSize, val=1):

        foundBees=[0]*bufferSize
        for p in peaks: foundBees[p]=val
        return foundBees

''' Pasarle los buffers de ambos sensores'''
def countBees(interior, exterior):

    intSuave, inP = findPeaks(interior)
    extSuave, exP = findPeaks(exterior)

    detectados = []
    for pico in inP:
            for x in exP:
                delta = pico-x
                #print(pico,",",x,":",delta)
                if abs(delta) < maxDelta and abs(delta)>=0 :
                    detectados.append(int((x+pico)/2))
                    break
    return detectados, inP, exP, intSuave, extSuave

#contador con UN electrodo
def countBeesMono(sensorData):

    suave, peaks = findPeaks(sensorData)
    print(peaks)
    return  peaks, suave
   
