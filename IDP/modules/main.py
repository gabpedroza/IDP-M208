'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.line_following import Follower
from utime import sleep, ticks_ms


robot = Follower([4, 5, 7, 6,26,20,21,27], thresh = 0.99)
print("imhere")
while True:
    #time1 = ticks_ms()
    for i in range(10):
        robot.lineSensors.get_new_values()
    #print(ticks_ms() - time1)
    #sleep(9999)
    avg = robot.lineSensors.get_averages()
    print(avg)
    robot.make_correction(avg)
    












