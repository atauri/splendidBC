# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

'''
Métodos para probar algoritmos de conteo sobre buffers de muestras recibidos por POST desde el front
'''
from bottle import route, run, post, response, request, static_file
from importlib import reload 
import requests
import json


'''for CORS from web requests'''
def allow_cors(func):
    def wrapper(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*' # * in case you want to be accessed via any website
        return func(*args, **kwargs)
    return wrapper

'''Set buffer in range 0..127 if its in range 0..1
captures can be in range 0..1'''
def desnormalizar(buff):
    if (max(buff['interior'])<=1):
        buff['interior'] = [int(i*127) for i in buff['interior']]
        buff['exterior'] = [int(i*127) for i in buff['exterior']]
    return buff

'''buffer gets raw data from counter electrodes (only one escape!)'''
def getBufferFromUrlRequest(rq):    
    data = False
    try:
        bufferUrl = rq.POST['buffer']
        r = requests.get(bufferUrl)
        data = json.loads(r.text)
        #data = desnormalizar(data) # put in range 0..127
    except Exception as e: print(e)
    return data

# COUNTING ALGORITHM'S TO TRY...
# THEY RECEIVE A BUFFER OF RAW DATA 
'''{
    'interior':[...],
    'exterior':[...]
}'''
#return an array of same length as buffer with  mark whwere a bee is detected (ex 1)
# just to display it in user interface 
'''{
    'bees':[0,0,0,0,0,1,0,0....]
}'''

# Search for peaks i buffers whit scipy library
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
@allow_cors
def peaks(buffer):

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
    for i in range(len(buffer['exterior'])):
        combi.append(buffer['exterior'][i]*buffer['interior'][i])

    combi =  suavizar(combi)
    peaks, _ = find_peaks(combi, height=.25, prominence=.2, distance=100)
    
    print(peaks)
    for p in peaks:
        combi[p] = 0 # make a mark for the UI

    print(len(peaks)) # number of found peaks

    r={
        "bees": combi.tolist(), # this will be area chart
        "totalBees": len(peaks)
    }
    return json.dumps(r) # serialize

@allow_cors
def myCountingAlgorithm(buffer):
   
    bees=[0] * len(buffer['interior']) 
    
    ''' 
    
     
           YOUR CODE HERE

           
     
    '''
    r={
        "bees": bees, # a serie
        "totalBees": 0 # number of found bees
    }
    return json.dumps(r) # serialize

'''Called from testingSw/front ---> countBees button'''
@post('/countBees')
@allow_cors
def countBees():
    buffer = getBufferFromUrlRequest(request)  # get data
    
    return peaks(buffer) # Comment to try your own algorithm
    return myCountingAlgorithm(buffer) # Uncomment to try your own algorithm

run(host='0.0.0.0', server="paste", port=8008)


