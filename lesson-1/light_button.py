from machine import Pin
import time
INTERVAL = 0.01


button = Pin(13, Pin.IN, Pin.PULL_UP)
led = Pin(18, Pin.OUT)

while True:
  if button.value() == 0:
    led.value(1)
  else:
    led.value(0)

  time.sleep(INTERVAL)

