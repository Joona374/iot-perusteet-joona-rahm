from machine import Pin
import time
import dht

sensor = dht.DHT22(Pin(18))

while True:
    sensor.measure()
    temp = sensor.temperature()
    humid = sensor.humidity()
    print(f"Temp: {temp:.2f}c - Humid: {humid:.2f}%")
    time.sleep(2)