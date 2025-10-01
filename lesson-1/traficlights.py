from machine import Pin
import utime

INTERVAL = 0.1

R_LED = Pin(2, Pin.OUT)
Y_LED = Pin(3, Pin.OUT)
G_LED = Pin(4, Pin.OUT)
BUZZER = Pin(21, Pin.OUT)
BUTTON = Pin(18, Pin.IN, Pin.PULL_DOWN)

def turn_on_led(led_color):
    R_LED.value(0)
    Y_LED.value(0)
    G_LED.value(0)
    
    if led_color == "R":
        R_LED.value(1)
    elif led_color == "Y":
        Y_LED.value(1)
    elif led_color == "G":
        G_LED.value(1)

def switch_to_walking():
    turn_on_led("R")

    for _ in range(6):
        BUZZER.toggle()
        utime.sleep(1)

    turn_on_led("G")


def step_lights(time):
    if time <= 2:
        turn_on_led("G")
    elif time <= 3:
        turn_on_led("Y")
    elif time <= 5:
        turn_on_led("R")
    else:
        turn_on_led("Y")

def main():
    time = 0

    while True:
        if BUTTON.value() == 1:
            switch_to_walking()
            time = 0
        
        else:
            step_lights(time)
            time += INTERVAL
            if time > 6:
                time = 0

        utime.sleep(INTERVAL)

main()
