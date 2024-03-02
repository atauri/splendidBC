import board
import busio
import time

from adafruit_cap1188.i2c import CAP1188_I2C
i2c = busio.I2C(board.SCL, board.SDA)

cap = CAP1188_I2C(i2c)


def leer():
    for _ in range(1000):
        
        for i in range(1,8,2):
            x = cap[i].raw_value/127.
            y = cap[i+1].raw_value/127.0
            v= x*y
            #print(str(v)+", ",)

print("1000") 
inicio = time.time()    
leer()
fin = time.time()
print(fin-inicio)
print("fin")
