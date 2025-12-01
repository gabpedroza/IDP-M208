"""classes for all 3 distance sensors, used for different purposes"""

#import dependencies
from utime import sleep
from machine import Pin, I2C, SoftI2C, ADC

#these dependencies are from /libs - distance sensor libraries not in the standard library
from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701
from libs.VL53L0X.VL53L0X import VL53L0X

class FrontDistance:
    """TMF8x01 used as front distance sensor. Proximity mode. Detects when the object is no more than 5mm away."""
    def __init__(self, i2c:I2C, arrival_distance = 10):
        """initialize the sensor on robot setup by passing the i2c"""

        #arrival parameter
        self.arrival_distance = arrival_distance

        # Set the correct device
        device = "TMF8701"

    # Use the correct one - TODO can we auto detect this?
        if device == "TMF8701":
            self.sensor = DFRobot_TMF8701(i2c_bus=i2c)
        elif device == "TMF8801":
            self.sensor = DFRobot_TMF8801(i2c_bus=i2c)
        else:
            raise RuntimeError(f"Device {device} not known")
        
        #initialize the sensor
        print("Initialising ranging sensor TMF8x01......")
        while(self.sensor.begin() != 0):
            print("   Initialisation failed")
            sleep(0.3)
            sleep(0.2)
        print("   Initialisation done.")

    def get_distance(self):
        """simple wrapper for getting the current distance using proximity mode and throwing away bad data"""
        
        #start recording values and once there is a value return it
        self.sensor.start_measurement(self.sensor.eMODE_NO_CALIB, mode = self.sensor.ePROXIMITY)

        got_valid_value = False
        while not got_valid_value:
            if(self.sensor.is_data_ready() == True):
                value = self.sensor.get_distance_mm()
                if value != 0:
                    got_valid_value = True
        return value

class LeftDistance:
    """Left distance sensor for detecting boxes on the side. Use VL53L0X"""
    def __init__(self, i2c: I2C, sampling_interval_s = 0.03, box_thresh_mm=280):
        
        self.sampling_interval_s = sampling_interval_s
        self.data = []
        self.box_thresh = box_thresh_mm

        #configure sensor setup
        self.sensor = VL53L0X(i2c)
        #leave these alone
        self.sensor.set_Vcsel_pulse_period(self.sensor.vcsel_period_type[0], 18)
        self.sensor.set_Vcsel_pulse_period(self.sensor.vcsel_period_type[1], 14)

    def get_current_distance(self):
        """record the distance at a specific moment and return it too. sensor needs to be active"""
        distance = self.sensor.read()
        self.data.append(distance)
        return distance
    
    def determine_if_box(self, n_samples = 10) ->bool:
        """check for box using rolling average of last n samples + this one"""
        box = False
            
        #wait for enough samples before starting to determine if box
        #no box ~350
        #wall/scaffolding ~310
        #box ~250-270
        if len(self.data) > n_samples-1:
            ave_range = self.data[-n_samples:] #get the last 10 elements

            #compute rolling average
            total = 0
            for sample in ave_range:
                total += sample
            rolling_average = total / n_samples

            #determine if box
            if rolling_average < self.box_thresh:
                box = True
                #if we found a box, clear data as well
                self.data = []

        #return box status - will return false if there weren't enough samples
        return box

class RightDistance:
    """ultrasonic sensor. not used yet! But will be used for box detection so similar algo to left distance"""
    def __init__(self, adc: ADC, multiplier=3900):
        #initialize the sensor, parameters, data
        self.sensor=adc
        self.data = []
        self.multiplier=multiplier
    
    def get_current_distance(self, sampling_interval_s=0.04) -> float:
        """read the current distance from the sensor and add to the data list as well."""
        dist = self.sensor.read_u16()*self.multiplier/65535 #convert to mm
        self.data.append(dist)
        #give it a rest that is enough for the 30 Hz max polling rate
        sleep(sampling_interval_s)

        #append and return
        self.data.append(dist)
        return dist
    
    def determine_if_box(self, n_samples=10) -> bool:
        """check for box using rolling average of last n samples + this one"""
        #NOTE: direct copy + paste of code from other sensor
        #TODO: calibrate
        box = False
            
        #wait for enough samples before starting to determine if box
        #no box ~350
        #wall/scaffolding ~310
        #box ~250-270
        if len(self.data) > n_samples-1:
            ave_range = self.data[-n_samples:] #get the last 10 elements

            #compute rolling average
            total = 0
            for sample in ave_range:
                total += sample
            rolling_average = total / n_samples

            #determine if box
            if rolling_average < 280:
                box = True

        #return box status - will return false if there weren't enough samples
        return box



#########test

def test_front():  
    #start by initializing the appropriate i2c bus and then starting the sensor
    i2c_bus = SoftI2C(sda=Pin(20), scl=Pin(21), freq=100000)
    front_sensor = FrontDistance(i2c_bus)

    #keep polling till we arrive
    has_arrived = False
    while True:
        distance = front_sensor.get_distance()
        print(f"current distance = {distance} mm")
        
        #check for arrival
        if distance < front_sensor.arrival_distance:
            has_arrived = True
            print(f"ARRIVED! with distance {distance}")

def test_left():
    #initialize the sensor, record data manually using get_distance and determine_if_box, keep displaying status
    
    #i2c
    i2c_bus = I2C(id=0, sda=Pin(20), scl=Pin(21))
    
    #initialize sensor instance
    left_sensor = LeftDistance(i2c_bus,sampling_interval_s=0.03)

    box = False
    while not box:
        curr_dist = left_sensor.get_current_distance()
        box = left_sensor.determine_if_box(n_samples=10)
        print(f"current distance = {curr_dist}")
    
    #once we got a box we get here
    print("Box!!!")

def test_right():
    #initialize
    adc = ADC(Pin(28)) #must use a pin with ADC, here using GP28 (pin 34)
    right_sensor = RightDistance(adc)

    #box detection same as left
    box=False
    while not box:
        curr_dist = right_sensor.get_current_distance()
        box = right_sensor.determine_if_box()
        print(f"Current distance = {curr_dist}")
    
    #now got box
    print("Box!!")


if __name__ == '__main__':
   test_front()
   # test_left()
   #test_right()