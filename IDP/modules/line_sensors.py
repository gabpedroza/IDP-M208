'''collect data from line sensors and format to a binary list.'''
#NOTE: line sensor data comes in from a GPIO port and will be either logic HIGH or LOW. HIGH => light (on line) and LOW otherwise

from machine import Pin

class LineSensors:

    #static variables for data across samples
    front_data: list[int] = []
    left_data: list[int] = []
    right_data: list[int] = []
    rear_data: list[int] = []

    '''for collecting data from line sensors'''
    def __init__(self, front_pin, left_pin, right_pin, rear_pin) -> None: #collect port values for all sensors. Use GPXX number rather than jumper number
        #initialize pin instances from each sensor
        self.front_sensor = Pin(front_pin, Pin.IN, Pin.PULL_DOWN) #TODO: Determine whether to pull up or down
        self.left_sensor = Pin(left_pin, Pin.IN, Pin.PULL_DOWN)
        self.right_sensor = Pin(right_pin, Pin.IN, Pin.PULL_DOWN)
        self.rear_sensor = Pin(rear_pin, Pin.IN, Pin.PULL_DOWN)

    def get_new_values(self) -> None:
        '''Appends current values (0 or 1) from all 4 sensors and adds to respective lists'''
        #poll sensors for values. 1 for white and 0 for black
        self.front_data.append(self.front_sensor.value())
        self.left_data.append(self.left_sensor.value())
        self.right_data.append(self.right_sensor.value())
        self.rear_data.append(self.rear_sensor.value())
        return
        
    def get_averages(self) -> list[float]:
        '''average the values from all the sensors and clear data, call this after a certain number of loops of get_new_values'''
        #error handling for if we try to average an empty list
        if self.front_data == [] or self.left_data == [] or self.right_data == [] or self.rear_data == []:
            raise Exception("sensors have not collected any data")

        else: #main averaging
            front_sum = 0
            for x in self.front_data:
                front_sum += x
            front_average = front_sum / len(self.front_data)

            left_sum = 0
            for x in self.left_data:
                left_sum += x
            left__average = left_sum / len(self.left_data)

            right_sum = 0
            for x in self.right_data:
                right_sum += x
            right_average = right_sum / len(self.right_data)

            rear_sum = 0
            for x in self.rear_data:
                rear_sum += x
            rear_average = rear_sum / len(self.rear_data)

            #now clean up the static lists to empty them
            self.front_data, self.left_data, self.right_data, self.rear_data = [], [], [], []

            #now return the averages
            return [front_average, left__average, right_average, rear_average]

