#!/home/pi/Documents/telepython/.env/bin/python3

import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
relay = 12
GPIO.setup(relay,GPIO.OUT)
GPIO.setup(37,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(relay, 0)

while 1:
    tombol = GPIO.input(37)
    if tombol == 0:
        print("Pintu dibuka")
        GPIO.output(relay, 1)
        time.sleep(4)
        GPIO.output(relay, 0)  