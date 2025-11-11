'''collect data from line sensors and format to a binary list.'''
# Note: line sensor data comes in from a GPIO port and will be either logic HIGH or LOW. HIGH => light (on line) and LOW otherwise

from machine import Pin
from utime import sleep

class LineSensors:
    '''for collecting data from line sensors'''
    def __init__(self, front_pin, left_pin, right_pin, rear_pin) -> None: #collect port values for all sensors. Use GPXX number rather than jumper number
        #initialize pin instances from each sensor
        self.front_sensor = Pin(front_pin, Pin.IN, Pin.PULL_DOWN) #TODO: Determine whether to pull up or down
        self.left_sensor = Pin(left_pin, Pin.IN, Pin.PULL_DOWN)
        self.right_sensor = Pin(right_pin, Pin.IN, Pin.PULL_DOWN)
        self.rear_sensor = Pin(rear_pin, Pin.IN, Pin.PULL_DOWN)

    def get_values(self) -> list:
        '''Gets current values (0 or 1) from all 4 sensors and outputs as list [front, left, right, rear]'''
        #poll sensors for values. 1 for white and 0 for black
        front_value = self.front_sensor.value()
        left_value = self.left_sensor.value()
        right_value = self.right_sensor.value()
        rear_value = self.rear_sensor.value()
        
        # return list as per spec
        values = [front_value, left_value, right_value, rear_value]
        return values
        
