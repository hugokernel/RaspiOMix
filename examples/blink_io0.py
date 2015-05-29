from raspiomix import Raspiomix
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(Raspiomix.IO0, GPIO.OUT)

while True:
    GPIO.output(Raspiomix.IO0, not GPIO.input(Raspiomix.IO0))
    time.sleep(1)
