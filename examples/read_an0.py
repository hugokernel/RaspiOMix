from raspiomix import Raspiomix
import time

r = Raspiomix()

while True:
    print "%f Volt !" % r.readAdc(0)
    time.sleep(1)
