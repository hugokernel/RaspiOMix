RaspiOMix
=========

A RaspberryPi board with 5V tolerance and Grove compatible.

Specifications
--------------

- 4 general 5V tolerant input / output
- 4 analog input, 0-5V, 18 bit resolution (MCP3424)
- 2 digital input via DIP switch
- Real Time Clock with battery backup (DS1307)
- 2 I2C external connector
- 1 serial external connector
- Power input via jack

Python example :

    >>> from raspiomix import Raspiomix
    >>> r = Raspiomix()
    >>> r.readRtc()
    2014-11-12T20:41:26
    >>> print(r.readAdc(0))
    [4.0669732000000005]
    >>>print(r.readAdc((0, 1, 2, 3)))
    [4.066934600000001, 0.010923800000000001, 0.08515160000000001, 0.2866822]

--

Une carte fille pour RaspberryPi avec entrées / sorties tolérantes au 5V et des connecteurs compatible Grove.

Caractéristiques
----------------

- 4 entrées / sorties tolérantes 5V
- 4 entrées analogiques, 0-5V, 18 bits de résolution (MCP3424)
- 2 entrées numériques via DIP switch
- Horloge temps réel avec batterie de sauvegarde (DS1307)
- 2 connecteurs pour I2C
- 1 connecteur pour communication série
- Alimentation via jack
