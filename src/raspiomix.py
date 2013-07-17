#!/usr/bin/python

import time
#import serial
import string, random
import quick2wire.i2c as i2c

import RPi.GPIO as GPIO

class Raspiomix:

    IO0 = 7
    IO1 = 11
    IO2 = 13
    IO3 = 15

    ADC_I2C_ADDRESS = 0x6E

    DEVICE = '/dev/ttyAMA0'

    def __init(self):
        pass

class Raspiomix_Test(Raspiomix):

    def __init__(self):
        # Init mode
        GPIO.setmode(GPIO.BOARD)

        #GPIO.setup(self.IO1, GPIO.IN)
        #GPIO.setup(self.IO2, GPIO.IN)
        #GPIO.setup(self.IO3, GPIO.IN)

        #GPIO.add_event_detect(self.IO1, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)
        #GPIO.add_event_detect(self.IO2, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)
        #GPIO.add_event_detect(self.IO3, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)

    def out(self):
        GPIO.setup(self.IO0, GPIO.OUT)
        GPIO.setup(self.IO1, GPIO.OUT)
        GPIO.setup(self.IO2, GPIO.OUT)
        GPIO.setup(self.IO3, GPIO.OUT)

        while True:
            GPIO.output(self.IO0, GPIO.HIGH)
            GPIO.output(self.IO1, GPIO.HIGH)
            GPIO.output(self.IO2, GPIO.HIGH)
            GPIO.output(self.IO3, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.IO0, GPIO.LOW)
            GPIO.output(self.IO1, GPIO.LOW)
            GPIO.output(self.IO2, GPIO.LOW)
            GPIO.output(self.IO3, GPIO.LOW)
            time.sleep(0.5)

    def int(self):
        GPIO.setup(self.IO0, GPIO.IN)
        GPIO.setup(self.IO1, GPIO.IN)
        GPIO.setup(self.IO2, GPIO.IN)
        GPIO.setup(self.IO3, GPIO.IN)
#        GPIO.add_event_detect(self.current, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)
        GPIO.add_event_detect(self.IO0, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)
        GPIO.add_event_detect(self.IO1, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)
        GPIO.add_event_detect(self.IO2, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)
        GPIO.add_event_detect(self.IO3, GPIO.BOTH, callback = self.interrupt, bouncetime = 300)

        while True:
            time.sleep(2)

    def serial(self):
        ser = serial.Serial(self.DEVICE, 9600, timeout = 1)

        while True:
            character = random.choice(string.letters)
            print("Send " + character)
            ser.write(character)
            print("Read " + ser.read())
            time.sleep(1)

    def analog(self):

        varDivisior = 64 # from pdf sheet on adc addresses and config
        varMultiplier = (3.3/varDivisior)/1000

        with i2c.I2CMaster() as bus:
            def changechannel(address, adcConfig):
                bus.transaction(i2c.writing_bytes(address, adcConfig))

            def getadcreading(address):
                h, m, l ,s = bus.transaction(i2c.reading(address,4))[0]
                while (s & 128):
                    h, m, l, s = bus.transaction(i2c.reading(address,4))[0]
                # shift bits to product result
                t = ((h & 0b00000001) << 16) | (m << 8) | l
                # check if positive or negative number and invert if needed
                if (h > 128):
                    t = ~(0x020000 - t)
                return t * varMultiplier

            while True:
                changechannel(self.ADC_I2C_ADDRESS, 0x9C)
                print ("Channel 1: %02f" % getadcreading(self.ADC_I2C_ADDRESS))
                changechannel(self.ADC_I2C_ADDRESS, 0xBC)
                print ("Channel 2: %02f" % getadcreading(self.ADC_I2C_ADDRESS))
                changechannel(self.ADC_I2C_ADDRESS, 0xDC)
                print ("Channel 3: %02f" % getadcreading(self.ADC_I2C_ADDRESS))
                changechannel(self.ADC_I2C_ADDRESS, 0xFC)
                print ("Channel 4: %02f" % getadcreading(self.ADC_I2C_ADDRESS))
                print('--')
                time.sleep(0.5)

    def interrupt(self, index):
        if index == self.IO0:
            print("Event detected on IO0 !")
        elif index == self.IO1:
            print("Event detected on IO1 !")
        elif index == self.IO2:
            print("Event detected on IO2 !")
        elif index == self.IO3:
            print("Event detected on IO3 !")

if __name__ == '__main__':

    r = Raspiomix_Test()
    r.analog()
#    r.out()
#    r.serial()
#    r.prepareEvent()
#    while True:
#        time.sleep(2)



