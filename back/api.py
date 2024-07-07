from bottle import route, run, post, response, request, static_file
from importlib import reload 
import json
import requests
import glob

 

def allow_cors(func):
    """ this is a decorator which enable CORS for specified endpoint """
    def wrapper(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*' # * in case you want to be accessed via any website
        return func(*args, **kwargs)
    return wrapper


'''list of bc samples for validation'''
@route('/samples')
@allow_cors
def getSamples():
    
    files = glob.glob("/var/www/html/splendid/samples/*.mp4")
    r=[]
    for f in files: 
        r.append( f[f.rindex("/")+1:-4] )
    #print(r)
    return json.dumps(r)



'''Lista los VIDEOS de puturudefua.es/splendid/capturas'''
urlCapturas = "http://puturrudefua.es/splendid/"

@route('/capturas')
@allow_cors
def getCapturas():
    
    x = requests.get(urlCapturas+'index.php')
    
    files= x.text.replace(",]", "]")
    files = json.loads(files)
    nombres = []
    
    for f in files:
        #print(f)
        try:
            n= f[:f.index('.')]
            if len(n) ==20: nombres.append(n)
        except: pass
    nombres = list(set(nombres))
    nombres.sort()
    print(nombres)
    return json.dumps(nombres)


''' Recupera un buffer de datos subido a puturrudefua.es/splendid/capturas'''
@route('/buffer/<nombre>')
@allow_cors
def getBuffer(nombre):
   
    u = urlCapturas+"capturas/"+nombre
    print(u)
    r = requests.get(u)
    print("-------------------------")
    return json.loads(r.text)



run(host='0.0.0.0', server="paste", port=8008)