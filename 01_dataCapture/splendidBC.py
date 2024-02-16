'''Splendid Bee Counter
Conetca por el puerto serie y rellena un buffer'''

import serial # pip install pyserial
import time
import patronaje


# SETUP ======================================
mac= "/dev/tty.usbserial-0001" #mac
win = "COM19" #win
what = win # con quien se conecta
NIVELES = 9
mostrarValores = False
pserie= None # puerto serie
tamBuffer = 10000 #con delay .5 milis en el sensor
#================================================


i = 0
'''el cono tiene 2 electrodos'''
buffer=[]
buffer2=[]

esperandoDatos = True
leyendo = False

def normalizar(x):
    if (x<=0): return 0
    return float(x/127)

def get():
    ser = pserie
    global i
    global leyendo 
    global esperandoDatos

    leyendo = True
    esperandoDatos = True

    global buffer
    global buffer2

    ## esperar a que el sensor sute la basura
    while esperandoDatos:
        c="."
        try:
            c = int(ser.readline().rstrip())
            b = int(c) # si no es un numero salta
            esperandoDatos = False
            print("GO!")    
        except Exception as e: 
            print(c)
        
    '''rellenar el buffer
        primero un electrodo y luego el otro 
        FALTA: mecanismo de sincronización'''
    start = time.time()
    while i<tamBuffer:
        #leer el dato ---------
        try:
            '''el electrodo interior es positivo y el exterior es negativo'''

            x=int(ser.readline().rstrip())
            y=int(ser.readline().rstrip())

            if x >= 0: 
                b = x
                b2 = y*(-1)
            else:
                b=y
                b2=x*(-1)
            b = normalizar(b)
            b2 = normalizar(b2)    
        
        except Exception as e: 
            print("Exception al recibir datos de ESP "+str(e))
            b=0
            b2=0
        if mostrarValores:
            print(b)
            print(b2)
            print("----")       
        buffer.append(b)
        buffer2.append(b2)
        
        i+=1 
        if(i%100==0): print(tamBuffer-i)
    leyendo = False
    print("dejo de leer")
    end = time.time()
    print(end - start)
    patronaje.buffer = buffer
    patronaje.buffer2 = buffer2
    

'''conexion con el puerto serie'''
def conectar():
    con = False
    while not con:
        try:
            ser = serial.Serial(port=what,  baudrate=115200)
            con = ser.isOpen()
            print("conexion con esp OK")
        except Exception as e:
            print(e)
            time.sleep(1)
    return ser

"""================================================"""
pserie=conectar()
