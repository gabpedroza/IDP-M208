from machine import Pin
from utime import sleep

pin = Pin(18, Pin.OUT)

print("LED starts flashing...")

pin.on()
sleep(20000)