from machine import Pin
import utime

pir = Pin(28, Pin.IN)

while True:
  if pir.value() == 1:
    print("SOS")

  utime.sleep(1)