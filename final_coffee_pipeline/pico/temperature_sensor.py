from machine import ADC, Pin
import math
import config

class Thermometer:
  def __init__(self):
    self.adc = ADC(Pin(config.PINS["temp_sensor_pin"]))
    self.conf = config.TEMP

  def read_temp(self):
      v = self.adc.read_u16() / 65535 * 3.3
      # correct divider orientation for Wokwi’s NTC
      r_ntc = self.conf["r_fixed"] * (v / (3.3 - v))
      temp_k = 1 / (
          1 / self.conf["t0"]
          + (1 / self.conf["beta"]) * math.log(r_ntc / self.conf["r0"])
      )
      temp_c = temp_k - 273.15
      return round(temp_c, 1)

