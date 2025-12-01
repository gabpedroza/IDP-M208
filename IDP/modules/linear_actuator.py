from machine import Pin, PWM
from utime import sleep, time

#constants determined on calibrating linear actuator (TODO)
PREPARATION_TIME = 6.5#5.4 #seconds
EXTENSION_SPEED = 25 #out of 100 #for now assume retraction same as extension
RETRACTION_SPEED = EXTENSION_SPEED
LIFTING_TIME = 7.2
DROP_TIME = 23
RESET_TIME = 25


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

    def prepare_fork(self) -> None:
        """extend the forklift to a level suitable for inserting into the box. about 1.5cm"""
        #box will be lifted by extending, going forward to lift the box and then retracting.

        #extend actuator for a certain amount of time
        for i in range(EXTENSION_SPEED + 1):
            self.set(0, i)
            sleep(0.01)
        self.set(0, EXTENSION_SPEED)
        sleep(PREPARATION_TIME)
        for i in range(EXTENSION_SPEED + 1):
            self.set(0, 50 - i)
            sleep(0.01)
    
    def lift_box(self) -> None:
        """retract the fork partially to pick up the box"""
        for i in range(RETRACTION_SPEED + 1):
            self.set(1, i)
            sleep(0.01)
        self.set(1, RETRACTION_SPEED)
        sleep(LIFTING_TIME)
        for i in range(RETRACTION_SPEED + 1):
            self.set(1, 50 - i)
            sleep(0.01)

    def drop_box(self) -> None:
        """extend the fork a lot to drop the box"""
        for i in range(EXTENSION_SPEED + 1):
            self.set(0, i)
            sleep(0.01)
        self.set(0, EXTENSION_SPEED)
        sleep(DROP_TIME)
        for i in range(EXTENSION_SPEED + 1):
            self.set(0, 50 - i)
            sleep(0.01)
    
    def reset_fork(self) -> None:
        """reset to zero extension from any position"""
        for i in range(RETRACTION_SPEED + 1):
            self.set(1, i)
            sleep(0.01)
        self.set(1, RETRACTION_SPEED)
        sleep(RESET_TIME)
        for i in range(RETRACTION_SPEED + 1):
            self.set(1, 50 - i)
            sleep(0.01)

if __name__ == '__main__':
    actuator = LinearActuator(0,1)
    actuator.reset_fork()

