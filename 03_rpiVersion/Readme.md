# Raspberry Pi Software

## Pi Zero 2w IMPORTANT NOTES

* Instalar **bookworm 64 bits**
* Aumentar el tamño de swap para arreglar [Vs-code CRASH](https://pimylifeup.com/raspberry-pi-swap-file/)
  
* COPIAR CARPETA DE RPI A LOCAL

    > scp -r tadu@192.168.1.203:/home/tadu/splendid . 


* una vez conectado CAP1188 por i2c se puede saber si está bien conectado y su direccion con

    > i2cdetect -y 1

    ![alt text](image.png)

    Si conecto 2 módulos hay que crear en python los objetos pasándole la dirección i2c

## Python libraries

primero instalar virtualenv, hacer un entorno y activarlo
A continuación instalar librerías de requirements.txt

Empollarse la librería de [cap1188](https://docs.circuitpython.org/projects/cap1188/en/latest/)

## Aplicaciones disponibles

* **count.py** Cuenta los 4 escapes e inserta en MQTT con la mac del dispositivo
* **validate.py** Selcciona un escape (de momento en código) y envía el buffer y las abejas encontradas por el socket a validateFront.html

## TO-DO list

* Separar la funcion findPeaks
* Invertir la curva para encontrar los valles en lugar de los picos
* Ajustar los parámetros (desde la interfaz?)
* Seleccionar escape desde la interfaz
* Ajustar parámetros del módulo CAP1188
* Hacer copias de seguridad de la tarjeta
* Poner tarjeta en modo lectura
* Añadir RTC y hacer copia local de los datos