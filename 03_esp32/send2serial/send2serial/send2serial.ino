// Copyright 2024 David Atauri
// SPDX-License-Identifier: CC-BY-NC-SA-1

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_CAP1188.h>

// PINOUT ---------------------------------
#define BUZZZER_PIN 2 // buzzer
#define CAP1188_RESET  9 // Reset Pin is used for I2C or SPI
#define CAP1188_CS  10 // CS pin is used for software or hardware SPI

// cap1188 to counter electrodes
// A
//static byte registrosExt[4]={16,20,18,22};
//static byte registrosInt[4]={17,21,19,23};

// contador B
static byte registrosExt[4]={16,18,20,23};
static byte registrosInt[4]={17,19,21,22};

// cap1188 sensibility ----------------------
#define SENS1 0x00 // less
#define SENS2 16
#define SENS3 0x2F // DEFAULT
#define SENS4 0x3F
#define SENS5 0x4F //more sensibility

// some config vars....
#define pausa 4 //delay between readings
//float base = 0.25*127; // Min thershold)

Adafruit_CAP1188 cap = Adafruit_CAP1188();

void beep(int beeps){
  for (int j=0; j<beeps; j++){
    digitalWrite(BUZZZER_PIN,HIGH);
    delay(50);
    digitalWrite(BUZZZER_PIN,LOW);
    delay(50);
  }
}

// -------------------------------------------
void setup() {

  Serial.begin(115200);
  pinMode(BUZZZER_PIN,OUTPUT); 
  Serial.begin(115200);
  delay(500);

  // connect counter  
  while (!cap.begin()) {
    Serial.println("CAP1188 not found");
    delay(1000);
  }
  Serial.println("CAP1188 found!");
  beep(3);//ready!
}


// -------------------------------------------
void loop(){

    int8_t  x = 0;
    int8_t  y = 0;
    
    // iterate through 4 escapes
    // it sends x0,y0, x1,y1, x2, y2, x3, y3, \n
    for (int t=0; t<4; t++){

      //select electrode (NO STATIC !!)
      byte s1 = registrosInt[t];
      byte s2 = registrosExt[t];

      //read electrodes! will get something -127..127  
      x = cap.readRegister(s1);
      y = cap.readRegister(s2);

      if (x<0) x=0;
      if(y<0) y=0;

      //send to .py  
      
      // send each elctrode serated
      /*
      Serial.print(x);
      Serial.print(",");
      Serial.print(y);
      Serial.print(","); 
      */

      // send two ectrodes multiplied and normalized
      // good for peak finding
      Serial.print((x/127.)*(y/127.)); //one escape in one float 0..1
      Serial.print(",");
    
    }
    Serial.println("");    
   delay(pausa);
}