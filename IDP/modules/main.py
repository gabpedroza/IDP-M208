'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.line_following import Follower
from utime import sleep
from machine import Pin

BUTTON_PIN = 19

#far left, left, right, far right
robot = Follower([4, 5, 7, 6,14, 11,10,8,0,0,20,21,16,17,18,19], thresh = 0.5)
print("imhere")
robot.walk(0.6)

# global variable that determines whether the robot is on or off
activated = False

# function that is called when button is pressed
def handle_interrupt(pin):
    global activated
    if not activated:
        activated = True
        
    if activated:
        activated = False
            
# variable for the button pin    
pir = Pin(BUTTON_PIN,Pin.IN)

# calls the interrupt function when button is pressed
pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

# main loop that checks if the global variable activated is off


while True:
        
    if activated:
        #time1 = ticks_ms()
        for i in range(10):
            robot.lineSensors.get_new_values()
        #print(ticks_ms() - time1)
        #sleep(9999)
        avg = robot.lineSensors.get_averages()
        print(avg)
        robot.algorithm_ground(avg)
    













