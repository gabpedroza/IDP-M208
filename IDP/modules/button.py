"""NB: FILE NOT USED. really simple button wrapper"""
from machine import Pin

class Button:
    def __init__(self, pin):
        self.btn = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.activated = False

    def check_state(self) -> None:
        """check the status of the button"""
        self.activated = self.btn.value()

def button_isr(pin):
    global activated

    print("Button Pressed")

def test_button():
    button = Pin(19, Pin.IN)

    button.irq(trigger=Pin.IRQ_RISING,handler=button_isr)

    button.on()

    while True:
        pass




if __name__ == '__main__':
    test_button()