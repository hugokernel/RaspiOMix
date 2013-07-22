#!/usr/bin/python

import time
import serial
import string, random
import quick2wire.i2c as i2c

import RPi.GPIO as GPIO

class Raspiomix:

    IO0 = 7
    IO1 = 11
    IO2 = 13
    IO3 = 15

    DIP0 = 12
    DIP1 = 16

    I2C_ADC_ADDRESS = 0x6E
    I2C_RTC_ADDRESS = 0x68

    DEVICE = '/dev/ttyAMA0'

