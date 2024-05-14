'''Apply find to samples stored in json files'''

import peaksLib
import glob
import json

path = "/var/www/html/splendid/samples/"

def iterateOverFiles():

    files = glob.glob(path+"*.json")
    
    for f in files: 
        
        file = open(f, 'r' )
        data = json.loads(file.read())
        file.close()

        #print(data)
        for escape in range(4):
            smoothed, peaks = peaksLib.findPeaks(data[escape]['mix'])
            print(peaks)
            peaksSerie = peaksLib.drawPeaks(peaks, len(data[escape]['mix']))
            data[escape]['peaks'] = {
                "serie":peaksSerie,
                "peaks": len(peaks),
                "smoothed":smoothed
            } 
        #print(data)    
        print("------------------------")

        file = open(f, 'w' )
        file.write(json.dumps(data))
        file.close()
        
iterateOverFiles()