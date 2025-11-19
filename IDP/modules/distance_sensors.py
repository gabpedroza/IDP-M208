"""classes for all 3 distance sensors, used for different purposes"""

#import dependencies
from utime import sleep
from machine import Pin, I2C, SoftI2C

#these dependencies are from /libs - distance sensor libraries not in the standard library
from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701

class FrontDistance:
    """TMF8x01 used as front distance sensor. Proximity mode. Detects when the object is no more than 5mm away."""
    def __init__(self, i2c:SoftI2C, arrival_distance = 5):
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
    def __init__(self):
        

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

if __name__ == '__main__':
    test_front()