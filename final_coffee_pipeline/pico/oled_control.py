# oled_controller.py

from machine import Pin, I2C
import ssd1306

class OledController():
    def __init__(self):
        self.i2c = I2C(0, scl=Pin(17), sda=Pin(16))
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.current_lines = []

    def write_row(self, text_row: str):
        if len(self.current_lines) < 6:
            self.current_lines.append(text_row)
            self._write_current_lines()
        else:
            print("OLED SCREEN FULL, CLEAR FIRST")

    def add_to_last_row(self, text: str):
        self.current_lines[-1] = self.current_lines[-1] + text
        self._write_current_lines()

    def _write_current_lines(self):
        self.oled.fill(0)
        for i, line in enumerate(self.current_lines):
            self.oled.text(line, 0, i*10)
        try:
            self.oled.show()
        except Exception as e:
            pass

    def clear_screen(self):
        self.oled.fill(0)
        self.current_lines = []



oled = OledController()