'''collect data from line sensors and format to a binary list.'''
#NOTE: line sensor data comes in from a GPIO port and will be either logic HIGH or LOW. HIGH => light (on line) and LOW otherwise

from machine import Pin

class LineSensors:

    #static variables for data across samples
    far_left_data: list[int] = []
    left_data: list[int] = []
    right_data: list[int] = []
    far_right_data: list[int] = []

    '''for collecting data from line sensors'''
    def __init__(self, far_left_pin, left_pin, right_pin, far_right_pin) -> None: #collect port values for all sensors. Use GPXX number rather than jumper number
        #initialize pin instances from each sensor
        self.far_left_sensor = Pin(far_left_pin, Pin.IN, Pin.PULL_DOWN) 
        self.left_sensor = Pin(left_pin, Pin.IN, Pin.PULL_DOWN)
        self.right_sensor = Pin(right_pin, Pin.IN, Pin.PULL_DOWN)
        self.far_right_sensor = Pin(far_right_pin, Pin.IN, Pin.PULL_DOWN)

    def get_new_values(self) -> None:
        '''Appends current values (0 or 1) from all 4 sensors and adds to respective lists'''
        #poll sensors for values. 1 for white and 0 for black
        self.far_left_data.append(self.far_left_sensor.value())
        self.left_data.append(self.left_sensor.value())
        self.right_data.append(self.right_sensor.value())
        self.far_right_data.append(self.far_right_sensor.value())
        return
        
    def get_averages(self) -> list[float]:
        '''average the values from all the sensors and clear data, call this after a certain number of loops of get_new_values'''
        #error handling for if we try to average an empty list
        if self.far_left_data == [] or self.left_data == [] or self.right_data == [] or self.far_right_data == []:
            raise Exception("sensors have not collected any data")

        else: #main averaging
            far_left_sum = 0
            for x in self.far_left_data:
                far_left_sum += x
            far_left_average = far_left_sum / len(self.far_left_data)

            left_sum = 0
            for x in self.left_data:
                left_sum += x
            left__average = left_sum / len(self.left_data)

            right_sum = 0
            for x in self.right_data:
                right_sum += x
            right_average = right_sum / len(self.right_data)

            far_right_sum = 0
            for x in self.far_right_data:
                far_right_sum += x
            far_right_average = far_right_sum / len(self.far_right_data)

            #now clean up the static lists to empty them
            self.far_left_data, self.left_data, self.right_data, self.far_right_data = [], [], [], []

            #now return the averages
            return [far_left_average, left__average, right_average, far_right_average]

