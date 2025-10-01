from machine import Pin
import utime
import random

button = Pin(28, Pin.IN, Pin.PULL_DOWN)
led = Pin(20, Pin.OUT)

timer_start = 0

def button_handler(pin):
    led.value(0)
    button.irq(handler=None)

    reaction_time = utime.ticks_diff(utime.ticks_ms(), timer_start)
    print(f"Reaction time: {reaction_time} ms.")

delay = random.uniform(2, 5)
utime.sleep(delay)
led.value(1)
print("CLICK!")

timer_start = utime.ticks_ms()

button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)