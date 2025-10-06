# main.py
import utime
import machine

from device_controller import DeviceController
import config

device = DeviceController()
device.init_device()

while True:
    device.connectivity_loop()          # handles wifi + mqtt + check_msg

    if not config.FLAGS["making_coffee"]:
        device.make_coffee_if_needed()

    device.update_oled_if_needed()


    device.sync_time_if_needed()
    device.read_temp_if_needed()

    # optional: ping cadence (harmless if offline; guarded inside ping)
    device.ping_mqtt_if_needed()

    utime.sleep_ms(config.LOOP["tick_ms"])
