'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.graph_model import Plant
from utime import sleep, ticks_ms
class Follower:
    '''figure out the situation the robot is in at a single time step, and apply correction'''
    def __init__(self, pins_assignment : list, thresh= 0.5, correction_functions = [lambda x: x, lambda x: x]):
        '''set variables on initialization. Pin ordering: motorLeft x 2, motorRight x2, (far left,left,right, far right) TTL
            correction_functions order: left, right'''

        #store inputs from the line sensors. These will already be processed to be binary (1 or 0). Format: front, left, right, rear
        self.thresh = thresh
        self.motorLeft = DCMotor(pins_assignment[0], pins_assignment[1], correction_functions[0])
        self.motorRight = DCMotor(pins_assignment[2], pins_assignment[3], correction_functions[1])
        self.lineSensors = LineSensors(pins_assignment[4], pins_assignment[5], pins_assignment[6], pins_assignment[7])
        self.tcount = 0
        self.turn_timer = [0,0,0,0]
        self.waiting= 0
        self.skip_time = 0.2
        self.node = 1
        self.orientation = 1
        self.plant = Plant()
        #TODO: set inputs from other sensors

    def detect_radical_turn(self, sensor_data):
        radical_turn = [False, False]
        for s in [0, 3]:
            if sensor_data[s] > self.thresh and self.waiting == 0: #first detection, start timer
                self.waiting = ticks_ms()
        if self.waiting != 0 and ticks_ms() - self.waiting >= 150: #check if sensors see white
            if sensor_data[0] > self.thresh:
                radical_turn[0] = True
            if sensor_data[3] > self.thresh:
                radical_turn[1] = True
            self.waiting = 0
               
        return radical_turn

    def pid(self, sensor_data):
            #pid
            error = sensor_data[2] - sensor_data[1]
            self.motorLeft.forward(60 + 40*error)
            self.motorRight.forward(60 - 40*error)

    def algorithm_ground(self, sensor_data):
        turns = {1: "right", 3: "left", 21: "right", 10:"front", 14:"front"}
        radical_turn = detect_radical_turn(sensor_data)
        if not radical_turn[0] and not radical_turn[1]:
            pid(sensor_data)
        else:
            if self.plant.nodes[self.node].modes["ground"][self.orientation]: #turn time
                if radical_turn[0] and radical_turn[1]:
                    self._turn(turns[self.node])
                elif radical_turn[0] and not radical_turn[1]:
                    self._turn("left")
                else radical_turn[1] and not radical_turn[0]:
                    self._turn("right")

            self.node = (self.node + 1)%23


    def make_correction(self, sensor_data: list): #TODO
        '''based on situation, use motors to apply a correction'''
        
        #decides whether there is a right-angle turn to be made
        #after the first detection of a sensor, it waits a fixed amount of time to give the robot the chance to
        #get the other side sensor to the same position, since it could be a cross.
        radical_turn = [False, False]
        for s in [0, 3]:
            if sensor_data[s] > self.thresh and self.waiting == 0: #first detection, start timer
                self.waiting = ticks_ms()
        if self.waiting != 0 and ticks_ms() - self.waiting >= 150: #check if sensors see white
            if sensor_data[0] > self.thresh:
                radical_turn[0] = True
            if sensor_data[3] > self.thresh:
                radical_turn[1] = True
            self.waiting = 0
               
        if (not radical_turn[0] and not radical_turn[1]): #if all black, PID
            #pid
            error = sensor_data[2] - sensor_data[1]
            self.motorLeft.forward(60 + 40*error)
            self.motorRight.forward(60 - 40*error)
        else:
            if radical_turn[0] and not radical_turn[1]: #it saw white on left (TLeft or plain left)
                if self.tcount <= 8 and self.tcount >= 3:
                    sleep(self.skip_time)
                if self.tcount == 10:
                    self._turn("left")
                if self.tcount == 11:
                    sleep(self.skip_time)
                if self.tcount == 12:
                    self._turn("left")
                if self.tcount <= 19 and self.tcount >= 14:
                    sleep(self.skip_time)
                if self.tcount == 20:
                    self._turn("left")
            elif radical_turn[1] and not radical_turn[0]: #saw white on right (TRight or plain right)
                if self.tcount == 1:
                    sleep(self.skip_time)
                if self.tcount == 21:
                    sleep(self.skip_time)
                if self.tcount == 22:
                    self._turn("right")
                    self.walk(1.5, 100)
                    self.walk(999, 0)
            else: #saw white on both sides (cross or T)
                if self.tcount == 0:
                    self._turn("right")
                if self.tcount == 2:
                    self._turn("left")
                if self.tcount == 9:
                    sleep(self.skip_time)
                if self.tcount == 13:
                    sleep(self.skip_time)
            self.tcount += 1
            
    def _turn(self, direction, speed = 100, delay1 = 0.6, delay2 = 0.5):
        '''turns the robot 90deg. Direction is either "left" or "right".
            delay1 is the time of the actual turn, delay2 is the move time it moves front before turning'''
        self.motorLeft.forward(speed)
        self.motorRight.forward(speed)
        sleep(delay2)
        if(direction == "left"):
            self.orientation = (self.orientation-1)%4
            self.motorLeft.reverse(speed)
            self.motorRight.forward(speed)
            sleep(delay1)
        elif(direction == "right"):
            self.orientation = (self.orientation+1)%4
            self.motorLeft.forward(speed)
            self.motorRight.reverse(speed)
            sleep(delay1)
        else:
            pass
    def walk(self, delay, speed = 100):
        '''Moves forwards (speed > 0) or backwards (speed < 0). Can stop with speed == 0'''
        if(speed > 0):
            self.motorLeft.forward(speed)
            self.motorRight.forward(speed)
        else:
            self.motorLeft.reverse(speed)
            self.motorRight.reverse(speed)
        sleep(delay)



