# Counting algorithm development an testing

Counting algorithm is -with the case desing and signal captura- the core of the project. This application is intended to develop,
test and improve this algorithm.



## What is this for...

This app allows you write a python function to  count bees in the buffer of raw data and test it over a bunch of files (video and data) from a real devie and a real hive

  * Se le proporcionan los buffers de los electrodos y
  * Recibe un Json con el número de abejas y en qué instante del video los ha encontrado
  * el algoritmo debe estar en recurso web estandarizado (POST)
  * Devolver también el tiempo que tarda en realizarse
  
## How to start

First see this brief [Youtube explanation](https://www.youtube.com/watch?v=Pkqkp8idgXs) (Use subtitles with translation if you can't speak spanish)

Here is How I work:

* Open the project in VsCode (must have installed extension "live server")
* create a python virtual env and install packages with pip

> python3 conteo.py 

* A bottle server will be started listening on por 8008
* Right click on front_capturas.htm -> open with live server (first install vscode extension)
* Choose a file in the left
* Click "count bees" to see the server response
* Each black line is a detected bee

## Known bugs

(to be fixed one day...)

* If you zoom to a border "play zoomed" won't work
  
## What's next

Once you happy with your counting function migrate it to your counting microcontrolles (maybe an ESP32 or a piZero, or whatever...)

## To-do list

* Move captures from puturrudefua to splendid server (titi)
* Store real bee counts on aditional file (something like YYYY_MM_DD__hh__mm__ss.info) and display is int the UI.