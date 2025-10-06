# config.py
import utime

LOOP = {
    "tick_ms": 100,
    "ping_interval": 5000,
    "time_sync_interval": 20000,
    "read_temp_interval": 10000
}

MQTT = {
    "publish_topic": "iot/demo/responses",
    "subscribe_topic": "iot/demo/commands"
}

WLAN = {
    "ssid": "Wokwi-GUEST",
    "password": ""
}

FLAGS = {
    "making_coffee": False,
    "last_ping": utime.ticks_ms(),
    "last_time_sync": utime.ticks_ms(),
    "last_read_temp": utime.ticks_ms(),
    "previous_time": None
}

TEMP = {
    "r_fixed": 10000,
    "beta": 3950,          # typical for 10k NTC
    "t0": 273.15 + 25,
    "r0": 10000
}

PINS = {
    "servo_pin": 27, 
    "servo_pin_freq": 50,
    "led_pin": 26,
    "temp_sensor_pin": 28
}