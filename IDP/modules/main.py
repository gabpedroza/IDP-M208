'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.line_following import Follower
from machine import Pin
from modules.distance_sensors import LeftDistance
from utime import sleep

BOX_CHECK_SAMPLES = 3

#motor left, motor right, far left, left, right, far right, linear actuatorx2, front distance, colour, button, left distance
robot = Follower([4, 5, 7, 6,14, 11,10,8, 0,1,20,21,16,17,18, 19,20,21], thresh = 0.5)
print("imhere")
sleep(2)
robot.walk(0.6)




# global variable that determines whether the robot is on or off
activated = False

# function that is called when button is pressed
def handle_interrupt(pin):
    global activated
    print("Button pressed!")
    if not activated:
        activated = True
        
    if activated:
        activated = False
    
    main()


# main loop that checks if the global variable activated is off
global final_node_timer
final_node_timer = 0    
            
# variable for the button pin    
#button = Pin(BUTTON_PIN,Pin.IN)

# calls the interrupt function when button is pressed
#button.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

# have to check if the script goes back to here, or if continues from where it was interrupted

def main():
    box=False
    prev_node = 4

    while True:
        if activated or True:
            #time1 = ticks_ms()
            for i in range(10):
                robot.lineSensors.get_new_values()
            #print(ticks_ms() - time1)
            #sleep(9999)
            avg = robot.lineSensors.get_averages()
            #print(avg)
            if box and (robot.detect_radical_turn(avg) in [[True, False], [False, True]]):
                robot.pick_ground_box()
                robot.deliver_box()
            
            else:
                robot.hunt_box(avg, "ground")

            #nodes 5 to 10 and 16 to 21 are the nodes where we could find box
            #BUT we want to stop checking shortly after reaching the last nodes, otherwise we will be checking up until the end of the straight
            if (robot.node in range(5,11) or robot.node in range(16,22)) and not box:
                print(robot.node)
                if robot.node > prev_node:
                    #when we reach a new node, stop the robot
                    robot.walk(0.1,speed=0)
                    #check distance 3 times for box detection
                    for _ in range(3):
                        dist=robot.leftDistance.get_current_distance()
                        sleep(0.03)
                        print(dist)
                    box = robot.leftDistance.determine_if_box(n_samples=BOX_CHECK_SAMPLES) #need to tune this according to how much time we have to see boxes (esp start and end box)
                    if box:
                        print("box found!")
                        #if we find a box, we now need to get it and return to the path which is all handled by one handy function
                        robot.pick_ground_box()
                        #now we need to deliver it. robot already knows what the colour is and will go accordingly.
                        robot.deliver_box()
                        #now the robot has delivered the box and is back where it started when it initially detected box. So on the next run of the loop we are just going to keep going from the top
                
                prev_node = robot.node

               
main()