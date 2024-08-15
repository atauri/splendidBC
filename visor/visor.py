import keyboard
import cv2
import json
#import peaksLib
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.animation as animation
import threading
import glob
import peaksLib

# insertar marca de abeja que sale
keyboard.add_hotkey('b', lambda: addBee(serie))

# write file
keyboard.add_hotkey('ctrl+w', lambda: save(serie, test))
# reset bees
keyboard.add_hotkey('ctrl+r', lambda: reset(serie))

# count bees (apply findPeaks function)
keyboard.add_hotkey('c', lambda: findBees(serie)) #COUNT

#play video
keyboard.add_hotkey('p', lambda: playVideo(test))


def save(s, f):
        print("\nSave ",f)
        s['suave'] = [] # jode el fichero
        file = open('./videos/'+f+".json", 'w')
        print(json.dumps(s))
        file.write(json.dumps(s))
        file.close()

def reset(s):
        print("reset")
        s['bees'] = [0]* len(s['sensor'])
        animate(0)

def findBees(serie):
        print("find bees")
        suave, peaks = peaksLib.findPeaks(serie['sensor'])
        print(peaks)
        fb = peaksLib.drawPeaks(peaks,len(serie['sensor']))
        #print(fb)
        serie['foundBees'] = fb
        serie['suave'] = suave

        animate(0)

def addBee(serie):
        print("Bee")
        global pos
        global vlength

        p= int(pos * len(serie['sensor'])/vlength)
        print("bee at ", p)
        serie['bees'][p] = 1
        

def playVideo(test):
        #lanzar en hilo
        threading.Thread(target=play, args=(test,)).start()

def play(f):
        
        global pos 
        global vlength
        global esperar
        global serie

        video="./videos/"+f+".mp4"
        print(video)
         
        cap = cv2.VideoCapture(video)
        if (cap.isOpened()== False): 
                print("No se abrió")
                
        else: 
                vlength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                print(vlength )
        pos=0

        #animation.FuncAnimation(fig, animate, interval=250)
        
        while cap.isOpened():
                ret, frame = cap.read()
                
                if ret == True:
                # Display the resulting frame
                        cv2.imshow('Frame', frame)
                        animate(pos)
                        
                # Press Q on keyboard to exit
                        if cv2.waitKey(25) & 0xFF == ord('q'):
                                break
                pos += 1
                if pos > vlength:
                        cap.release()
                        print("-------------------")                       
             
        pos = 0
        cap.release()
        cv2.destroyAllWindows()
        print("CERRADO")


def abrirDatos(f):

        print(f+".json")
        data = None
        with open("./videos/"+f+".json") as file:
                data = json.load(file)

        # si no existe la serie bees la crea vacia
        if 'bees' not in data.keys():
                print("crear serie bees")
                data['bees']=[0]*len(data['sensor'])
       
        if 'foundBees' not in data.keys():
                print("crear serie foundBees")
                data['foundBees']=[0]*len(data['sensor'])

        return(data)


def animate(i):

        #global pos
        global vlength
        global serie

        #print(i)
        tam = len(serie['sensor'])
        current = [0]*tam
        try:
                x = int(i*tam/vlength)
                current[x] = 1
                #print(x)
        except Exception as e:
                pass #print(e)

        ax.clear()

        info=test+" "

        ax.plot(serie['sensor'], color="gray", linewidth=.75)

        if "suave" in serie.keys(): 
                ax.plot(serie['suave'], color="black", linewidth=.75)
        # bees in video manually counted
        if "bees" in serie.keys(): 
                ax.plot(serie['bees'], color="red", linewidth=.75)
                info+="Bees:"+str(serie['bees'].count(1))
        if "foundBees" in serie.keys(): 
                ax.plot(serie['foundBees'], color="blue", linewidth=.75)
                info+=", Estimated:"+ str(serie['foundBees'].count(1))
        # video position
        
        ax.plot(current, color="blue", linewidth=.5)

        # info
        
        plt.text(0, 0, info)
        print(info)
        plt.show()
        

def files():
        videos = glob.glob('./videos/*.mp4')
        for i in range(len(videos)):
                name = videos[i][-20:-4]
                
                print(str(i)+" : ",name)

        index= int(input("video:"))
        return(videos[index][-20:-4])


test = files()
serie = abrirDatos(test)


#------------------------------------
pos = 0
vlength=10000 # se sobreescribe al leer el video

fig = plt.figure()
fig.set_size_inches(35, 4)

ax = fig.add_subplot(1, 1, 1)

animate(0)





