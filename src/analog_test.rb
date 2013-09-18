#!/usr/bin/env ruby

require "i2c"
require "i2c/i2c"
 
def init_i2c
  I2C.create("/dev/i2c-1")
end

def get_channels(i2c)
  channels = [0x9C,0xBC,0xDC,0xFC]
  values =   [ 0.0, 0.0, 0.0, 0.0]

  channels.each_with_index do |channel, index|
    # Read first analog channel
    #  puts "Switching to channel 0x#{channel.to_s(16).upcase}"
    i2c.write(0x6E,channel)

    # Read 4 bytes
    # The first byte should be all zeroes
    # The first bit of 4th byte (& 0x80) should be 0, indicating the measure is ready (Cf datasheet page 19)
    lsbs = i2c.read(0x6E,4).unpack("N").first
    while (lsbs & 0x80 != 0) do
      # Repeat reading until measurement is ready
      lsbs = i2c.read(0x6E,4).unpack("N").first
    end
    config = lsbs & 0xff
    lsbs_shifted = lsbs >> 8
    #	puts "debug: idx %s conf out %s conf in %s lsb_raw %s lsb_shf %s raw_reread %s" % [ index, channel, config, lsbs, lsbs_shifted, i2c.read(0x6E,4).unpack("N") ]

    # We have 38.6 µV per unit (using PGA = 1x, 18bits conversion, and given the voltage divider ratio on the daughterboard)
    voltage_in_volts = (lsbs_shifted * 38.6) / 1_000_000

    # puts "channel %s value is %s (%s lsbs)" % [ index, voltage_in_volts, lsbs_shifted ]
    values[index] = voltage_in_volts
  end
  values

end

i2c = init_i2c

while true do
  values = get_channels(i2c)
  puts "Voltages : %s | %s | %s | %s " % [ values[0], values[1], values[2], values[3] ] 
end
