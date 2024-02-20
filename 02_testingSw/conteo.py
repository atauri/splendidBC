# Copyright 2024 David Atauri
# SPDX-License-Identifier: CC-BY-NC-SA-1

'''
Este contien métodos para probar algoritmos de conteo sobre buffers de muestras recibidos por POST desde el front
'''
from bottle import route, run, post, response, request, static_file
from importlib import reload 
import requests
import json


'''for CORS from web requests'''
def allow_cors(func):
    """ this is a decorator which enable CORS for specified endpoint """
    def wrapper(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*' # * in case you want to be accessed via any website
        return func(*args, **kwargs)
    return wrapper

'''Let buffer between 0..127 if its in range 0..1
Some old captures are in the range 0..1'''
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
        data = desnormalizar(json.loads(r.text))
    except Exception as e: print(e)
    return data

# COUNTING ALGORITHM'S TO TRY...
# THEY RECEIVE A BUFFER OF RAW DATA 
'''{
    'interior':[...],
    'exterior':[...]
}'''
#return an array of ints with same langth as buffer with '1' whwere a bee is detected:
'''{
    'bees':[0,0,0,0,0,1,0,0....]
}'''

# Search for peaks buffer['exterior'] whit scipy library (Just demo)
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
@allow_cors
def peaks(buffer):
    from scipy.signal import find_peaks
    import numpy as np

    bees=[0] * len(buffer['interior']) 
    
    # sensor interior
    '''peaks, _ = find_peaks(buffer['interior'], height=50, distance=100)
    for p in peaks:
        bees[p] = 0.5
    '''
    peaks, _ = find_peaks(buffer['exterior'], height=50, distance=100)
    for p in peaks:
        bees[p] = 1

    print(len(peaks))
    r={
        "bees": bees
    }
    #print(r)
    return json.dumps(r)

@allow_cors
def myCountingAlgorithm(buffer):
   
    bees=[0] * len(buffer['interior']) 
    
    ''' 
    
     
           YOUR CODE HERE

           
     
    '''
    r={
        "bees": bees
    }
    return json.dumps(r) # make a string

'''Called from testingSw/front ---> countBees button'''
@post('/countBees')
@allow_cors
def countBees():
    buffer = getBufferFromUrlRequest(request)  # get data
    
    return peaks(buffer) # Comment to try your own algorithm
    return myCountingAlgorithm(buffer) # Uncomment to try your own algorithm

run(host='0.0.0.0', server="paste", port=8008)


