'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.line_following import Follower
from utime import sleep

#far left, left, right, far right
robot = Follower([4, 5, 7, 6,14, 11,10,8,0,0,20,21,16,17,18,19], thresh = 0.5)
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
    
















