import network
import utime
from oled_control import oled
import config

wlan = None

def connect_to_wlan(timeout_ms=10000):
    """Initial Wi-Fi connect with OLED feedback."""
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WLAN["ssid"], config.WLAN["password"])

    oled.write_row("Connecting To")
    oled.write_row("Wi-Fi...")

    t0 = utime.ticks_ms()
    while not wlan.isconnected() and utime.ticks_diff(utime.ticks_ms(), t0) < timeout_ms:
        oled.add_to_last_row(".")
        utime.sleep(0.5)

    if wlan.isconnected():
        oled.write_row("Connected!")
        utime.sleep(1.0)
        return True
    else:
        oled.write_row("Wi-Fi Failed")
        return False

def wifi_is_up():
    """Return True only if WLAN object exists and link is active."""
    global wlan
    return wlan is not None and wlan.isconnected()

def ensure_wifi(ssid, password, timeout_ms=8000):
    """Reconnect if disconnected."""
    global wlan
    if wlan is None:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
    if wlan.isconnected():
        return True
    wlan.connect(ssid, password)
    t0 = utime.ticks_ms()
    while not wlan.isconnected() and utime.ticks_diff(utime.ticks_ms(), t0) < timeout_ms:
        utime.sleep_ms(200)
    return wlan.isconnected()
