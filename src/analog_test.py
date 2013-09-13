
import sys, tty, copy
from raspiomix import Raspiomix
import quick2wire.i2c as i2c


def testAnalog():

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

        chan = raw = [ 0, 0, 0, 0 ]
        channels = [ 0x9C, 0xBC, 0xDC, 0xFC ]
        while True:
            for i in range(0, 4):
                changechannel(Raspiomix.I2C_ADC_ADDRESS, channels[i])
                raw[i] = getadcreading(Raspiomix.I2C_ADC_ADDRESS)
                chan[i] = round(raw[i], 2)

            print ("Chan 0: %0.2f, 1: %0.2f, 2: %0.2f, 3: %0.2f" % (chan[0], chan[1], chan[2], chan[3]))

    print("[Analog test done !]")

print("""
   __                 _   ___ _      _
  /__\ __ _ ___ _ __ (_) /___( )\/\ (_)_  __
 / \/// _` / __| '_ \| |//  ///    \| \ \/ /
/ _  \ (_| \__ \ |_) | / \_/// /\/\ \ |>  <
\/ \_/\__,_|___/ .__/|_\___/ \/    \/_/_/\_\\
               |_|""")

testAnalog()

print("\n")
print("\n")

