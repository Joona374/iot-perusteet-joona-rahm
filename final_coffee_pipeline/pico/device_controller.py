#device_controller-py
import utime, machine, json

from servo import ServoController
from oled_control import oled
from wlan_utils import connect_to_wlan, ensure_wifi, wifi_is_up
from dyiumqtt import MQTTClient
from temperature_sensor import Thermometer

import config

class DeviceController:
    def __init__(self):
        self.mqtt = MQTTClient(self.on_mqtt_msg)
        self.servo = ServoController()
        self.oled = oled
        self.temp_sensor = Thermometer()
        self.timer_set_for = None
        self.duration_set = None
        self.status = "IDLE"
        self._next_mqtt_attempt = utime.ticks_ms()  # backoff gate
        self._last_oled_update = utime.ticks_ms()


    def init_device(self):
        connect_to_wlan()

        # Retry loop for MQTT connect
        while True:
            try:
                self.mqtt.connect()
                break
            except Exception as e:
                print("MQTT connect failed, retrying in 1s:", e)
                utime.sleep_ms(1000)
        self.mqtt.subscribe(config.MQTT["subscribe_topic"])

        self.get_time_from_server()

    def connectivity_loop(self):
        # 1) Wi-Fi first
        if not wifi_is_up():
            ok = ensure_wifi(config.WLAN["ssid"], config.WLAN["password"], timeout_ms=6000)
            if not ok:
                # try again in ~2s
                self._next_mqtt_attempt = utime.ticks_add(utime.ticks_ms(), 2000)
                return

        # 2) MQTT connect/backoff
        if (self.mqtt.sock is None) and utime.ticks_diff(utime.ticks_ms(), self._next_mqtt_attempt) >= 0:
            try:
                self.mqtt.connect()
                self.mqtt.subscribe(config.MQTT["subscribe_topic"])
            except Exception as e:
                print("Reconnect failed:", e)
                self._next_mqtt_attempt = utime.ticks_add(utime.ticks_ms(), 2000)
                return

        # 3) Service MQTT (drain PINGRESP / messages)
        if self.mqtt.sock:
            self.mqtt.check_msg()

    def on_mqtt_msg(self, topic, msg):
        if topic == "iot/demo/commands":
            try:
                cmd_data = json.loads(msg)
                self.handle_command(cmd_data)
            except Exception as e:
                print("Error with: MSG:", e)     

    def handle_command(self, cmd_data: dict):
        command = cmd_data.get("command") 
        if command == "MAKE_COFFEE_NOW":
            p = cmd_data.get("param", {})
            duration = p.get("duration", 10)
            self._make_coffee_now(duration)    
        
        elif command == "SET_TIME":
            self._set_time(cmd_data)

        elif command == "SET_TIMER":
            self._set_timer(cmd_data)

        elif command == "CHECK_STATUS":
            self._check_status(cmd_data)

    def _make_coffee_now(self, duration=None):
        print("Making coffee!")
        self.oled.clear_screen()
        self.oled.write_row("MAKING COFFEE")

        self.duration_set = duration or 3  # default 3 min if not provided
        self.status = "MAKING_COFFEE"
        config.FLAGS["making_coffee"] = True

        self.brew_started_at = utime.time()  # <-- record start
        print(self.duration_set)
        print(self.status)
        
        self.servo.turn_switch_on()

    def get_brew_time_left(self):
        """Return seconds remaining in brew, or 0 if done / not brewing."""
        if self.status != "MAKING_COFFEE" or self.brew_started_at is None:
            print("Issue with brw time")
            return 0

        elapsed = utime.time() - self.brew_started_at
        remaining = self.duration_set * 60 - elapsed
        if remaining < 0:
            remaining = 0
        return int(remaining)

    def _set_time(self, cmd_data: dict):
        p = cmd_data.get("param", {})

        y = int(p.get("y", 1970))
        m = int(p.get("m", 1))
        d = int(p.get("d", 1))
        H = int(p.get("H", 0))
        M = int(p.get("M", 0))
        S = int(p.get("S", 0))

        # weekday is ignored (set 0)
        machine.RTC().datetime((y, m, d, 0, H, M, S, 0))

    def _set_timer(self, cmd_data: dict):
        p = cmd_data.get("param", {})

        y = int(p.get("y", 1970))
        m = int(p.get("m", 1))
        d = int(p.get("d", 1))
        H = int(p.get("H", 0))
        M = int(p.get("M", 0))
        S = int(p.get("S", 0))

        # weekday is ignored (set 0)
        self.timer_set_for = (y, m, d, 0, H, M, S, 0)
        self.duration_set = p.get("duration", None)
        self.status = "TIMER_SET"
        self.write_coffee_timers()
        self._check_status()

    def _check_status(self, cmd_data=None):
        if self.status == "TIMER_SET":
            self.mqtt.publish(config.MQTT["publish_topic"], "STATUS", {"STATUS": "TIMER_SET", "TIME": self.timer_set_for})
            return
        
        elif self.status == "MAKING_COFFEE":
            self.mqtt.publish(config.MQTT["publish_topic"], "STATUS", {"STATUS": "MAKING_COFFEE", "TIME_LEFT": self.get_brew_time_left()})
            return   

        self.mqtt.publish(config.MQTT["publish_topic"], "STATUS", self.status)


    def get_time_from_server(self):
        oled.clear_screen()
        self.mqtt.publish(config.MQTT["publish_topic"], "GET_TIME")

    def get_datetime_str(self, datetime_like, time_only=False):
        if datetime_like == None:
            return "--:--"
        else:          
            y, m, d, wd, H, M, S, _ = datetime_like
        
        if time_only:
            return f"{H:02d}:{M:02d}"

        return f"{H:02d}:{M:02d} {d:02d}/{m:02d}/{y}"


    def write_coffee_timers(self):
        self.oled.clear_screen()
        
        self.oled.write_row("Time:")
        self.oled.write_row(self.get_datetime_str(machine.RTC().datetime()))
        
        self.oled.write_row("Timer set for:")
        self.oled.write_row(self.get_datetime_str(self.timer_set_for))
        
        self.oled.write_row("Time left:")
        if self.timer_set_for:
            delta = self.get_delta_seconds()
            formated_delta = self.format_delta(delta)
            self.oled.write_row(formated_delta)
        else:
            self.oled.write_row("--:--")

    def make_coffee_if_needed(self):
        if not self.timer_set_for:
            return
        time_left = self.get_delta_seconds()
        if time_left <= 0:
            self._make_coffee_now()
        
    def get_delta_seconds(self):
        now_tuple = machine.RTC().datetime()
        now_secs = utime.mktime((now_tuple[0], now_tuple[1], now_tuple[2], now_tuple[4], now_tuple[5], now_tuple[6], 0, 0)) 
        target_secs = utime.mktime((self.timer_set_for[0], self.timer_set_for[1], self.timer_set_for[2], self.timer_set_for[4], self.timer_set_for[5], self.timer_set_for[6], 0, 0))
        delta = target_secs - now_secs
        return delta

    def format_delta(self, delta):
        if delta < 0:
            return "00h 00m"

        # Round to nearest minute
        delta = int((delta + 30) // 60) * 60

        days = delta // 86400
        hours = (delta % 86400) // 3600
        minutes = (delta % 3600) // 60

        if days > 0:
            return f"{days}d {hours:02d}h {minutes:02d}m"
        else:
            return f"{hours:02d}h {minutes:02d}m"

    def ping_mqtt_if_needed(self):
        self.mqtt.loop()
        if utime.ticks_diff(utime.ticks_ms(), config.FLAGS["last_ping"]) > config.LOOP["ping_interval"]:
            self.mqtt.ping()
            config.FLAGS["last_ping"] = utime.ticks_ms()

    def update_oled_if_needed(self):
        if utime.ticks_diff(utime.ticks_ms(), self._last_oled_update) < 5000:
            return
        self._last_oled_update = utime.ticks_ms()

        if self.status == "MAKING_COFFEE":
            remaining = self.get_brew_time_left()
            self.oled.clear_screen()
            self.oled.write_row("Brewing coffee...")
            self.oled.write_row(f"Time left: {remaining}s")

            if remaining <= 0:
                self.status = "COFFEE_DONE"
                self.timer_set_for = None
                self.duration_set = None
                config.FLAGS["making_coffee"] = False
                self.oled.write_row("Done!")
                self._check_status()
                self.servo.led_pin.toggle()
            return

        if config.FLAGS["previous_time"] != self.get_datetime_str(machine.RTC().datetime(), time_only=True):
            config.FLAGS["previous_time"] = self.get_datetime_str(machine.RTC().datetime(), time_only=True)
            self.write_coffee_timers()

    def sync_time_if_needed(self):
        if utime.ticks_diff(utime.ticks_ms(), config.FLAGS["last_time_sync"]) > config.LOOP["time_sync_interval"]:
            self.get_time_from_server()
            config.FLAGS["last_time_sync"] = utime.ticks_ms()

    def read_temp_if_needed(self):
        if utime.ticks_diff(utime.ticks_ms(), config.FLAGS["last_read_temp"]) > config.LOOP["read_temp_interval"]:
            current_temp = self.temp_sensor.read_temp()
            if self.mqtt.sock:
                self.mqtt.publish(config.MQTT["publish_topic"], "TEMP", current_temp)
            config.FLAGS["last_read_temp"] = utime.ticks_ms()