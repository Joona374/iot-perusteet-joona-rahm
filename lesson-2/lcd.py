import utime
from machine import Pin, I2C
from pico_i2c_lcd import I2cLcd

utime.sleep(1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

lcd = I2cLcd(i2c, 0x27, 4, 20)
lcd.putstr("Hello\nHello")