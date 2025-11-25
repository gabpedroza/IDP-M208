'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.line_following import Follower
from utime import sleep

#left motor, right motor, far left, left, right, far right, linear actuator, frotDistance, Colour
robot = Follower([4, 5, 7, 6,10, 11,14,8], thresh = 0.5)
print("imhere")
robot.walk(0.6)
while True:
    #time1 = ticks_ms()
    for i in range(10):
        robot.lineSensors.get_new_values()
    #print(ticks_ms() - time1)
    #sleep(9999)
    avg = robot.lineSensors.get_averages()
    print(avg)
    robot.algorithm_ground(avg)
    
















