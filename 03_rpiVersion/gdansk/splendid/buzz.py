
import RPi.GPIO as GPIO 
from time import sleep

GPIO.setmode(GPIO.BCM)
#Set buzzer - pin 17 as output
buzzer=17
GPIO.setup(buzzer,GPIO.OUT)

def beep(beeps=1):

    for _ in range(beeps):
        GPIO.output(buzzer,GPIO.HIGH)
        
        sleep(0.10) # Delay in seconds
        GPIO.output(buzzer,GPIO.LOW)
 
        sleep(.10)

