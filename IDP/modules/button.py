"""really simple button wrapper"""
from machine import Pin

class Button:
    def __init__(self, pin):
        self.btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.activated = False

    def check_state(self) -> None:
        """check the status of the button"""
        self.activated = self.btn.value()