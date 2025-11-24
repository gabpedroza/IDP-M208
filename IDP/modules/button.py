"""really simple button wrapper"""
from machine import Pin

class Button:
    def __init__(self, pin):
        self.btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)

    def pressed(self) -> bool:
        """check the status of the button and return True for pressed and False otherwise"""
        val = self.btn.value()

        if val == 1:
            return True
        return False