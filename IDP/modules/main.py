'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.line_following import Follower
from utime import sleep

#far left, left, right, far right
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

    #nodes 3 to 8 and 15 to 20 are the nodes where we could find box
    #BUT we want to start checking BEFORE we hit the first node of each sequence so start 1 early.
    if robot.node in [2,3,4,5,6,7,8] or robot.node in [14, 15,16,17,18,19,20]:
        box = robot.leftDistance.determine_if_box(n_samples=3)
        if box:
            #if we find a box, we now need to get it and return to the path which is all handled by one handy function
            robot.pick_ground_box()
            #now we need to deliver it. robot already knows what the colour is and will go accordingly.
            robot.deliver_box()
            #now the robot has delivered the box and is back where it started when it initially detected box. So on the next run of the loop we are just going to keep going from the top


