# servo.py
import utime
from machine import Pin, PWM
import config

class ServoController:
    MIN_MICRO_S = 500
    MAX_MICRO_S = 2500

    def __init__(self):
        self.servo_pin = PWM(Pin(config.PINS["servo_pin"]))
        self.servo_pin.freq(config.PINS["servo_pin_freq"])
        self.led_pin = Pin(config.PINS["led_pin"], Pin.OUT) # Just for simulating the switch on the coffee maker

    def _set_angle(self, angle: int):
        pulse_micro_s = self.MIN_MICRO_S + (angle / 180) * (self.MAX_MICRO_S - self.MIN_MICRO_S)
        pulse_fraction = pulse_micro_s / 20000
        duty_u16 = int(pulse_fraction * 65535)
        self.servo_pin.duty_u16(duty_u16)

    def turn_switch_on(self):
        print("TURNING THE COFFEE MACHINE ON")
        for i in range(31):
            self._set_angle(i)
            utime.sleep(0.05)
        
        self.led_pin.toggle() # Just for simulating the switch on the coffee maker
        print("THE COFFEE MACHINE IS ON")
        utime.sleep(0.5)

        for i in range(30, 0, -1):
                self._set_angle(i)
                utime.sleep(0.05)