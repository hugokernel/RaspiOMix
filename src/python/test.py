#!/usr/bin/python

import curses
import random
import string
import smbus
from copy import copy
from time import sleep

from raspiomix import Raspiomix
import serial
import RPi.GPIO as GPIO

raspi = Raspiomix()
IS_PLUS = raspi.isPlus()

info = None

GPIOS = (
    Raspiomix.IO0,
    Raspiomix.IO1,
    Raspiomix.IO2,
    Raspiomix.IO3,
)

if IS_PLUS:
    GPIOS += (
        Raspiomix.IO4,
        Raspiomix.IO5,
        Raspiomix.IO6,
        Raspiomix.IO7,
    )

GPIOS += (
    Raspiomix.DIP0,
    Raspiomix.DIP1
)

'''
 Channel #0 : [========================================================================================] 5.42
 Channel #1 : [=                                                                                       ] 0.01
 Channel #2 : [===                                                                                     ] 0.12
 Channel #3 : [=======                                                                                 ] 0.38
'''

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

'''
import time
for index in range(len(GPIOS)):
    GPIO.setup(GPIOS[index], GPIO.IN)
while True:
    current = [ 0 ] * len(GPIOS)
    for index in range(len(GPIOS)):
        current[index] = GPIO.input(GPIOS[index])
    print current
    time.sleep(1)
'''

def fillwin(w, c):
    y, x = w.getmaxyx()
    s = c * (x - 1)
    for l in range(y):
        w.addstr(l, 0, s)

def debug(string):
    db = curses.newwin(3, len(string) + 2, 5, 5)
    db.border()
    db.addstr(1, 1, string)
    db.touchwin()
    db.refresh()
    #db.getch()
    sleep(1)

class Window:
    pad = None
    size = []
    pos = []

    def refresh(self):
        self.pad.refresh(*self.pos)

    def clear(self):
        y, x = self.pad.getmaxyx()
        s = ' ' * (x - 2)
        for l in range(1, y):
            self.pad.addstr(l, 1, s)

class Input(Window):

    INPUT = 'i'
    OUTPUT = 'o'

    mode = INPUT
    output_level = 0

    STATE_LOW = '0'
    STATE_HIGH = '1'

    def __init__(self, height, width, pos):
        self.pos = pos
        self.pad = curses.newpad(height, width)
        self.pad.border()
        self.pad.addstr(0, 2, "Input / Output", curses.A_BOLD)
        self.pad.addstr(9, 3, "Press i or o key to switch In / Out")
        self.reset()

    def reset(self):
        self.last = [ -1 ] * len(GPIOS)
        self.current = [ 0 ] * len(GPIOS)

    def update(self, key = None):

        if key:
            if key == ord('i'):
                self.mode = self.INPUT
                self.clear()
                self.reset()
            if key == ord('o'):
                self.mode = self.OUTPUT
                self.clear()
                self.reset()

        # Clean line
        self.pad.addstr(2, 3, "           ")
        if self.mode == self.INPUT:

            for io in GPIOS:
                GPIO.setup(io, GPIO.IN)

            self.pad.addstr(2, 3, "Input mode", curses.A_UNDERLINE)

            #self.current = random.sample(range(5), 4)
            for index in range(len(GPIOS)):
                self.current[index] = GPIO.input(GPIOS[index])

            if self.last != self.current:
                self.pad.addstr(4, 3, "IO: ")
                #for channel in range(0, 4):
                for channel in range(len(GPIOS) - 2):
                    status = self.STATE_HIGH if self.current[channel] else self.STATE_LOW + ' '
                    self.pad.addstr(4, 8 + (channel * 5), "%i:%s" % (channel, status))

                self.pad.addstr(6, 3, "DIP:")
                i = 0
                for channel in range(len(GPIOS) - 2, len(GPIOS)):
                    status = self.STATE_HIGH if self.current[channel] else self.STATE_LOW + ' '
                    self.pad.addstr(6, 8 + (i * 5), "%i:%s" % (i, status))
                    i += 1
                self.last = copy(self.current)
            self.pad.refresh(*self.pos)
        elif self.mode == self.OUTPUT:

            for io in GPIOS:
                GPIO.setup(io, GPIO.OUT)

            self.pad.addstr(2, 3, "Output mode", curses.A_UNDERLINE)
            #for channel in range(0, 4):
            for channel in range(len(GPIOS) - 2):
                GPIO.output(GPIOS[channel], GPIO.HIGH if self.output_level else GPIO.LOW)
                status = self.STATE_HIGH if self.output_level else self.STATE_LOW + ' '
                information("status:%s, %i" % (status, self.output_level))
                self.pad.addstr(4 + channel, 3, "Channel #%i : %s" % (channel, status))

            self.output_level = 0 if self.output_level else 1
            self.pad.refresh(*self.pos)

class Analog(Window):

    last = [ -1 ] * 8
    current = [ 0 ] * 8

    MAX_VALUE = 5.0

    ADC_COUNT = 8 if IS_PLUS else 4

    def __init__(self, height, width, pos):
        self.pos = pos
        self.size = [ height, width ]
        self.pad = curses.newpad(height, width)
        self.pad.border()
        self.pad.addstr(0, 2, "Analog", curses.A_BOLD)

    def update(self, key = None):
        self.current = raspi.readAdc(range(self.ADC_COUNT))

        width = self.size[1]

        size = self.pad.getmaxyx()
        offset = int(((size[0] - 2) / 2) - 1)

        if self.last != self.current:
            for channel in range(self.ADC_COUNT):
                title = "Channel #%i : [%s] %0.2f   "

                bar = ''
                iteration = self.MAX_VALUE / (width - len(title) - 5)
                for i in range(0, width - len(title) - 3):
                    bar += ' ' if (round(self.current[channel], 2) == 0 or i * iteration > self.current[channel]) else '='

                self.pad.addstr(offset + channel, 3, title % (channel, bar, self.current[channel]))

            self.last = copy(self.current)
            self.pad.refresh(*self.pos)

class I2C(Window):

    EEPROM_ADDRESS = 0x50

    external_done = False
    internal_done = False

    def __init__(self, height, width, pos):
        self.pos = pos
        self.pad = curses.newpad(height, width)
        self.pad.border()
        self.pad.addstr(0, 2, "I2C", curses.A_BOLD)

    #def bcd2int(self, val):
    #    return ((val / 16 * 10) + (val % 16))

    def update(self, key = None):

        if key and key == ord('r'):
            self.external_done = False
            self.internal_done = False

        self.pad.addstr(9, 3, "Press r to reload")

        if self.internal_done == False:
            self.pad.addstr(2, 3, "Internal (RTC) :")

            try:
                self.pad.addstr(3, 3, '%s Ok !' % raspi.readRtc())

                self.internal_done = True

            except IOError:
                self.pad.addstr(3, 3, " - Writing, Reading : Ko (Maybe rtc_ds1307 module is loaded ?) !")
            finally:
                self.refresh()

        if self.external_done == False:
            self.pad.addstr(5, 3, "External (EEPROM) :")
            try:
                self.pad.addstr(6, 3, " - Writing")
                self.refresh()

                array = random.sample(range(10), 5)
                #array[0] = 0

                raspi.i2c.write_byte_data(self.EEPROM_ADDRESS, 0x00, array[0])

                sleep(0.05)

                read_results = raspi.i2c.read_byte_data(self.EEPROM_ADDRESS, 0x00)

                self.pad.addstr(6, 3, " - Writing, Reading")
                self.refresh()

                #for i in range(0, 4):
                if read_results != array[0]: #[i + 1]:
                    raise IOError
                
                self.pad.addstr(6, 3, " - Writing, Reading : Ok !")
                #self.pad.addstr(6, 3, '->' + '%s' % array[0] + ' %s' % read_results)

                self.external_done = True


                '''
                with i2c.I2CMaster() as bus:

                    self.pad.addstr(6, 3, " - Writing")
                    self.refresh()

                    array = random.sample(range(10), 5)
                    array[0] = 0

                    bus.transaction(
                        i2c.writing(self.EEPROM_ADDRESS, bytes(array)),
                    )

                    sleep(0.05)

                    self.pad.addstr(6, 3, " - Writing, Reading")
                    self.refresh()

                    read_results = bus.transaction(
                        i2c.writing_bytes(self.EEPROM_ADDRESS, 0x00),
                        i2c.reading(self.EEPROM_ADDRESS, 4)
                    )

                    for i in range(0, 4):
                        if read_results[0][i] != array[i + 1]:
                            raise
                    
                    self.pad.addstr(6, 3, " - Writing, Reading : Ok !")

                    self.external_done = True
                ''' 
            except IOError as e:
                self.pad.addstr(6, 3, " - Writing, Reading : Ko !")
                #self.pad.addstr(6, 3, str(e))
            finally:
                self.refresh()

class Serial(Window):

    ser = None

    def __init__(self, height, width, pos):
        self.pos = pos
        self.pad = curses.newpad(height, width)
        self.pad.border()
        self.pad.addstr(0, 2, "Serial", curses.A_BOLD)

        self.ser = serial.Serial(Raspiomix.DEVICE, 9600, timeout = 0.1)

    def update(self, key = None):

        rand = random.choice(string.ascii_letters)

        self.ser.write(rand.encode('utf8'))
        received = self.ser.read()

        if received:
            status = 'OK' if ord(received) == ord(rand) else 'KO'
        else:
            status = 'No response'

        self.pad.addstr(1, 3, "Send / Receive random data... %s          " % status)
        self.pad.refresh(*self.pos)


class Info(Window):

    def __init__(self, height, width, pos):
        self.pos = pos
        self.size = [ height, width ]
        self.pad = curses.newpad(height, width)
        self.pad.border()
        self.pad.addstr(0, 2, "Info", curses.A_BOLD)
        self.pad.addstr(1, 3, "Running on RaspiO'Mix" + ("+ Oh yeah ! ;)" if IS_PLUS else '') + "...")

    def update(self, key = None):
        status = 'OK'
        self.pad.refresh(*self.pos)
        self.pad.refresh(*self.pos)

def information(string):
    global info
    info.pad.addstr(1, 3, string.ljust(info.size[1] - 5))

def main(stdscr):
    global info

    key = None
    while key != ord('\n'):
        h, w = stdscr.getmaxyx()
        mh = int(h / 2)
        mw = int(w / 2)

        info = Info(3, mw, [ 0, 0, h - 3, mw, h, w ])
        info.update()

        input = Input(mh, mw, [ 0, 0, 0, 0, mh, mw ])
        i2c = I2C(mh, mw, [ 0, 0, 0, mw, mh, w ])
        analog = Analog(mh - 3, w, [ 0, 0, mh, 0, h, w ])
        serial = Serial(3, mw, [ 0, 0, h - 3, 0, h, w ])

        stdscr.nodelay(True)
        while key != ord('\n'):
            key = stdscr.getch()

            input.update(key)
            analog.update(key)
            i2c.update(key)
            serial.update(key)
            info.update(key)

            if key == curses.KEY_RESIZE:
                break

    stdscr.touchwin()
    stdscr.refresh()
    #stdscr.getch()

print("""   __                 _   ___ _      _
  /__\ __ _ ___ _ __ (_) /___( )\/\ (_)_  __
 / \/// _` / __| '_ \| |//  ///    \| \ \/ /
/ _  \ (_| \__ \ |_) | / \_/// /\/\ \ |>  <
\/ \_/\__,_|___/ .__/|_\___/ \/    \/_/_/\_\\
               |_|""")

curses.wrapper(main)

