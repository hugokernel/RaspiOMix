
import sys, tty, copy
from time import sleep
from raspiomix import Raspiomix
import serial
import RPi.GPIO as GPIO
import quick2wire.i2c as i2c
import curses

ios = [
    Raspiomix.IO0,
    Raspiomix.IO1,
    Raspiomix.IO2,
    Raspiomix.IO3
]


import random

GPIO.setmode(GPIO.BOARD)

def waitEnter():
    tty.setcbreak(sys.stdin)
    while True:
        if ord(sys.stdin.read(1)) == 10:
            break

def gpio(index):
    return GPIO.input(ios[index])
    #from random import randint
    #return randint(0, 1)

def testInput():
    for index in range(0, 4):
        GPIO.setup(ios[index], GPIO.IN)

        print("> Insert IO%i connector and switch input mode and press [Enter]" % index)
        waitEnter()

        status = list('[.....]')
        count = 1
        value, last = gpio(index), gpio(index)
        while True:
            sys.stdout.write("\r Switch between high and low level on input : %s   \r" % ("".join(status)) )
            sys.stdout.flush()
            sleep(0.1)
            value = gpio(index)

            if value == last:
                continue;

            last = value

            if value == 1:
                status[count] = '1'
            else:
                status[count] = '0'
            count += 1

            if count >= 7:
                break

        print("\n[Input %i : Ok !]" % index)
    print("Input test done !")

def testOutput():
    print("> Switch to output mode and press [Enter]")
    waitEnter()

    for index in range(0, 4):
        GPIO.setup(ios[index], GPIO.OUT)

        print("> Insert IO%i connector and switch input mode and press [Enter]" % index)
        waitEnter()

        print("Led must blink 5 times !")

        count = 0
        while True:
            GPIO.output(ios[index], GPIO.HIGH)
            sleep(0.3)
            GPIO.output(ios[index], GPIO.LOW)
            sleep(0.3)
            if count > 5:
                break

            count += 1

    print("[Output test done !]")

def testSerial():
    ser = serial.Serial(Raspiomix.DEVICE, 9600, timeout = 1)
    print("> Insert serial connector and press [Enter]")
    waitEnter()

    print("> Press random char (press [Enter] to exit)")

    while True:
        character = sys.stdin.read(1)
        if ord(character) == 10:
            break
        ser.write(character.encode('utf8'))
        print("Send %s, read %s" % (character, ser.read()))
        sleep(0.5)

    print("[Serial test done !]")

def testAnalog():

    varDivisior = 64 # from pdf sheet on adc addresses and config
    varMultiplier = (3.3/varDivisior)/1000

    print("> Insert analog connector and press [Enter]")
    waitEnter()

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

        chan = last = [ 0, 0, 0, 0 ]
        while True:
            changechannel(Raspiomix.ADC_I2C_ADDRESS, 0x9C)
            chan[0] = round(getadcreading(Raspiomix.ADC_I2C_ADDRESS), 2)

            changechannel(Raspiomix.ADC_I2C_ADDRESS, 0xBC)
            chan[1] = round(getadcreading(Raspiomix.ADC_I2C_ADDRESS), 2)

            changechannel(Raspiomix.ADC_I2C_ADDRESS, 0xDC)
            chan[2] = round(getadcreading(Raspiomix.ADC_I2C_ADDRESS), 2)

            changechannel(Raspiomix.ADC_I2C_ADDRESS, 0xFC)
            chan[3] = round(getadcreading(Raspiomix.ADC_I2C_ADDRESS), 2)

            for index in range(0, 4):
                if chan[index] != last[index]:
                    print ("Chan 0: %0.2f, 1: %0.2f, 2: %0.2f, 3: %0.2f" % (chan[0], chan[1], chan[2], chan[3]))
                    break

            last = copy.copy(chan)

    print("[Analog test done !]")

print("""
   __                 _   ___ _      _
  /__\ __ _ ___ _ __ (_) /___( )\/\ (_)_  __
 / \/// _` / __| '_ \| |//  ///    \| \ \/ /
/ _  \ (_| \__ \ |_) | / \_/// /\/\ \ |>  <
\/ \_/\__,_|___/ .__/|_\___/ \/    \/_/_/\_\\
               |_|""")

def printMenu():
    menu = [
        [ '1. Input' ],
        [ '2. Output' ],
        [ '3. Serial' ],
        [ '4. Analog' ],
        [ '5. Exit' ]
    ]

    print("Menu :")
    for m in menu:
        print(" " + m[0])

printMenu()

tty.setcbreak(sys.stdin)
while True:
    choice = sys.stdin.read(1)
    if choice == '1':
        testInput()
        printMenu()
    elif choice == '2':
        testOutput()
        printMenu()
    elif choice == '3':
        testSerial()
        printMenu()
    elif choice == '4':
        testAnalog()
        printMenu()
    elif choice == '5':
        exit(0)

print("\n")
print("\n")

