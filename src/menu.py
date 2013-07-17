#!/usr/bin/env python
import curses, os, copy

from raspiomix import Raspiomix
import serial
from time import sleep
import RPi.GPIO as GPIO
import quick2wire.i2c as i2c
import random

EEPROM_ADDRESS = 0x50

screen = curses.initscr() #initializes a new window for capturing key presses
curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
curses.start_color() # Lets you use colors when highlighting selected menu option
screen.keypad(1) # Capture input from keypad

# Change this to use different colors when highlighting
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
h = curses.color_pair(1) #h is the coloring for a highlighted menu option
n = curses.A_NORMAL #n is the coloring for a non highlighted menu option

GPIO.setmode(GPIO.BOARD)
IOS = [
    Raspiomix.IO0,
    Raspiomix.IO1,
    Raspiomix.IO2,
    Raspiomix.IO3
]

MENU = "menu"
COMMAND = "command"
CALLBACK = "callback"

def testInput():
    for index in range(0, 4):
        GPIO.setup(IOS[index], GPIO.IN)

    screen.nodelay(True)

    x = None
    while x != ord('\n'):
        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, menu_data['title'], curses.A_STANDOUT)

        screen.addstr(4, 4, 'Input test')

        for index in range(0, 4):
            status = GPIO.input(IOS[index])
            screen.addstr(6 + index, 4, 'Input #%i : %i' % (index, status))

        screen.refresh()
        sleep(0.5)

        x = screen.getch()

def testOutput():
    for index in range(0, 4):
        GPIO.setup(IOS[index], GPIO.OUT)

    screen.nodelay(True)

    x = None
    i = 0
    while x != ord('\n'):
        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, menu_data['title'], curses.A_STANDOUT)

        screen.addstr(4, 4, 'Output test')

        for index in range(0, 4):
            if i % 2:
                GPIO.output(IOS[index], GPIO.HIGH)
                screen.addstr(6 + index, 4, 'Output #%i : High' % index)
            else:
                GPIO.output(IOS[index], GPIO.LOW)
                screen.addstr(6 + index, 4, 'Output #%i : Low' % index)

        screen.refresh()
        sleep(0.5)

        x = screen.getch()
        i += 1

def testSerial():
    ser = serial.Serial(Raspiomix.DEVICE, 9600, timeout = 1)

    x = None
    while x != ord('\n'):
        try:
            screen.clear()
            screen.border(0)
            screen.addstr(2, 2, menu_data['title'], curses.A_STANDOUT)

            screen.addstr(4, 4, 'Serial test')

            if x != None:
                ser.write(chr(x).encode('utf8'))
                received = ser.read()
                if received:
                    screen.addstr(6, 4, 'Send %c, received %s : %s' % (chr(x), received, 'Ok' if x == ord(received) else 'Ko'))
                else:
                    screen.addstr(6, 4, 'No response !')

            screen.refresh()

            x = screen.getch()
        except:
            screen.addstr(9, 4, 'Error !')

def testAnalog():
    varDivisior = 64 # from pdf sheet on adc addresses and config
    varMultiplier = (3.3/varDivisior)/1000

    screen.nodelay(True)

    x = None
    Same = True
    chan = [ 0, 0, 0, 0 ]
    last = [ 0, 0, 0, 0 ]
    while x != ord('\n'):
        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, menu_data['title'], curses.A_STANDOUT)

        screen.addstr(4, 4, 'Analog test')

        for index in range(0, 4):
            screen.addstr(6 + index, 4, "Channel %i: %0.2f" % (index, chan[index]))

        screen.refresh()

        while Same and x != ord('\n'):
            x = screen.getch()

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
                        Same = False

        last = copy.copy(chan)
        Same = True

def testI2C():

    x = None
    while x != ord('\n'):
        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, menu_data['title'], curses.A_STANDOUT)

        screen.addstr(4, 4, 'I2C test')

        screen.addstr(6, 4, 'EEPROM address: 0x%x' % EEPROM_ADDRESS)
        screen.addstr(7, 4, 'Writing EEPROM...')
        screen.refresh()
        sleep(1)

        try:
            with i2c.I2CMaster() as bus:

                array = random.sample(range(10), 5)
                array[0] = 0

                bus.transaction(
                    i2c.writing(EEPROM_ADDRESS, bytes(array)),
                )

                screen.addstr(8, 4, 'Reading EEPROM...')
                screen.refresh()

                sleep(1)

                read_results = bus.transaction(
                    i2c.writing_bytes(EEPROM_ADDRESS, 0x00),
                    i2c.reading(EEPROM_ADDRESS, 4)
                )

                for i in range(0, 4):
                    if read_results[0][i] != array[i + 1]:
                        raise
                    else:
                        screen.addstr(9, 4, 'Ok !')
        except:
            screen.addstr(9, 4, 'Error !')
            sleep(2)
        finally:
            x = screen.getch()

menu_data = {
  'title': "RaspiO'Mix tester", 'type': MENU, 'subtitle': "Please selection an option...",
  'options': [
    { 'title': "Input",     'type': CALLBACK,   'callback': testInput },
    { 'title': "Output",    'type': CALLBACK,   'callback': testOutput },
    { 'title': "Serial",    'type': CALLBACK,   'callback': testSerial },
    { 'title': "I2C",       'type': CALLBACK,   'callback': testI2C },
    { 'title': "Analog",    'type': CALLBACK,   'callback': testAnalog }
  ]
}

# This function displays the appropriate menu and returns the option selected
def runmenu(menu, parent):

  # work out what text to display as the last menu option
  if parent is None:
    lastoption = "Exit"
  else:
    lastoption = "Return to %s menu" % parent['title']

  optioncount = len(menu['options']) # how many options in this menu

  pos=0 #pos is the zero-based index of the hightlighted menu option.  Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what option has been selected
  oldpos=None # used to prevent the screen being redrawn every time
  x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program

  # Loop until return key is pressed
  while x !=ord('\n'):
    if pos != oldpos:
      oldpos = pos
      screen.clear() #clears previous screen on key press and updates display based on pos
      screen.border(0)
      screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
      screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

      # Display all the menu items, showing the 'pos' item highlighted
      for index in range(optioncount):
        textstyle = n
        if pos==index:
          textstyle = h
        screen.addstr(5+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
      # Now display Exit/Return at bottom of menu
      textstyle = n
      if pos==optioncount:
        textstyle = h
      screen.addstr(5+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
      screen.refresh()
      # finished updating screen

    x = screen.getch() # Gets user input

    # What is user input?
    if x >= ord('1') and x <= ord(str(optioncount+1)):
      pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
    elif x == 258: # down arrow
      if pos < optioncount:
        pos += 1
      else: pos = 0
    elif x == 259: # up arrow
      if pos > 0:
        pos += -1
      else: pos = optioncount
    elif x != ord('\n'):
      curses.flash()

  # return index of the selected item
  return pos

# This function calls showmenu and then acts on the selected item
def processmenu(menu, parent=None):
    optioncount = len(menu['options'])
    exitmenu = False
    while not exitmenu: #Loop until the user exits the menu
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] == COMMAND:
            os.system(menu['options'][getin]['command']) # run the command
        elif menu['options'][getin]['type'] == MENU:
            processmenu(menu['options'][getin], menu) # display the submenu
        elif menu['options'][getin]['type'] == CALLBACK:
            menu['options'][getin]['callback']()

# Main program
processmenu(menu_data)
curses.endwin() #VITAL!  This closes out the menu system and returns you to the bash prompt.

