from scipy.signal import find_peaks
import numpy as np

# Setup ----
# smooth curve
witdh = 30
order = 2

# peak detection
peakHeight = .20
prominence = .2
peakWitdh = 50

def findPeaks(serie):

    # remove noise applying savgol filter
    def suavizar(serie):
        from scipy.signal import savgol_filter
        suave = savgol_filter(serie, window_length=witdh, polyorder=order)
        return suave
    
    suave =  suavizar(serie)
    #print(serie)
    peaks, _ = find_peaks(suave, height=peakHeight, prominence=prominence, distance=peakWitdh)
    #print(peaks)
    #print(len(peaks)) # number of found peaks
    return(suave, peaks)

def drawPeaks(peaks, bufferSize):
        foundBees=[0]*bufferSize
        for p in peaks: foundBees[p]=1
        return foundBees
