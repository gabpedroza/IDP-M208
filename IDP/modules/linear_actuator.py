from machine import Pin, PWM
from utime import sleep, time

#constants determined on calibrating linear actuator (TODO)
EXTENSION_TIME = 3 #seconds
EXTENSION_SPEED = 50 #out of 100
RETRACTION_TIME = EXTENSION_TIME #for now assume retraction same as extension
RETRACTION_SPEED = EXTENSION_SPEED


class LinearActuator:
    """class for setup and control of linear actuator, specific to the purpose of collecting box"""
    def __init__(self, dir_pin, pwm_pin):
        self.dir = Pin(dir_pin, Pin.OUT)  # set motor direction pin as an output
        self.pwm = PWM(Pin(pwm_pin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
    
    def set(self, dir: int, speed) -> None:
        """set actuator speed and direction. helper. Dir 0 for forward and 1 for reverse. Speed goes from 0 to 100"""
        self.dir.value(dir)  #set direction

        #error checking
        if (speed > 100) or (speed < 0):
            raise ValueError("Speed ranges from 0 to 100")

        #set speed
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor

    def extend_fork(self) -> None:
        """extend the forklift"""
        #box will be lifted by extending, going forward to lift the box and then retracting.

        #extend actuator for a certain amount of time
        start_time = time() #in seconds
        while time() < start_time + EXTENSION_TIME:
            self.set(0, EXTENSION_SPEED)
        self.set(0, 0) #to stop the actuator.

    def retract_fork(self) -> None:
        """exact opposite of extend. just retract the fork fully."""
        start_time = time() #in seconds
        while time() < start_time + RETRACTION_TIME:
            self.set(1, RETRACTION_SPEED)
        self.set(1, 0) #to stop the actuator.