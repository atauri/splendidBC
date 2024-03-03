# Software for Raspberry pi

## Pi Zero 2w IMPORTANT NOTES

* Instalar **bookworm 64 bits**
* Aumentar el swar para arreglar [Vs-code CRASH](https://pimylifeup.com/raspberry-pi-swap-file/)
  
* COPIAR CARPETA DE RPI A LOCAL

    > scp -r tadu@192.168.1.203:/home/tadu/splendid . 


* una vez conectado CAP1188 se puede saber si está bien conectado y su direccion con

    > i2cdetect -y 1

    ![alt text](image.png)

    Si conecto 2 módulos hay que crear en python los objetos pasándole la dirección i2c

## python libraries

primero instalar virtualenv, hacer un entorno y activarlo

Para poder conectar los sensores por i2c y leer en python añado las siguientes librerías: 

* adafruit-extended-bus==1.0.2
* adafruit-circuitpython-cap1188==1.3.12
* Scipi

## conectar en py

```py
import board
import busio
from adafruit_cap1188.i2c import CAP1188_I2C
i2c = busio.I2C(board.SCL, board.SDA)
````

