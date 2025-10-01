import time
from machine import Pin

def counter():
    for i in range(9):
        print(i)
        time.sleep(0.5)

def ask_for_name():
    name = input("What is your name?\n- ")
    if name == "Clark Kent":
        print("You are the Superman!")

    else:
        print("You are an ordinary person.")

def _flip_led(led):
    led.toggle()
    time.sleep(0.5)

def blink_led(pin_num: int, n = None):
    led = Pin(pin_num, Pin.OUT)

    if n:
        for _ in range(n):
            _flip_led(led)
        return

    while True:
        _flip_led(led)

def main():
    # Ensimmäiset WOKWIin tutstumis tehtävät
    counter()
    ask_for_name()
    blink_led(25, 8)
    blink_led(15, 8)

main()