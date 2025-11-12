from machine import Pin, PWM
from utime import sleep

class DCMotor:
    def __init__(self, dirPin, PWMPin):
        '''Initialises the servo motor at (dirPin, PWMPin). '''
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
        
    def off(self):
        
        self.pwm.duty_u16(0)
        
    def forward(self, speed=100):
        self.mDir.value(0)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor

    def reverse(self, speed=30):
        self.mDir.value(1)
        self.pwm.duty_u16(int(65535 * speed / 100))
        
class LinearActuator:
    def __init__(self, dirPin, PWMPin):
        '''Red wire on pin 1'''
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
           
    def set(self, dir, speed=100):
        '''Sets the extension of the motor. 0 = forward, 1 = reverse'''
        self.mDir.value(dir)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor
