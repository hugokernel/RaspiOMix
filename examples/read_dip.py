from raspiomix import Raspiomix
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(Raspiomix.DIP0, GPIO.IN)
GPIO.setup(Raspiomix.DIP1, GPIO.IN)

while True:
    print("DIP0: %s, DIP1: %s" % (GPIO.input(Raspiomix.DIP0, GPIO.input(Raspiomix.DIP1))))
    time.sleep(1)
