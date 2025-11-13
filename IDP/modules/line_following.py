'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from utime import sleep
class Follower:
    '''figure out the situation the robot is in at a single time step, and apply correction'''
    def __init__(self, pins_assignment : list, thresh= 0.5, correction_functions = [lambda x: x, lambda x: x]):
        '''set variables on initialization. Pin ordering: motorLeft x 2, motorRight x2, (front,left,right,rear) TTL
            correction_functions order: left, right'''

        #store inputs from the line sensors. These will already be processed to be binary (1 or 0). Format: front, left, right, rear
        self.thresh = thresh
        self.motorLeft = DCMotor(pins_assignment[0], pins_assignment[1], correction_functions[0])
        self.motorRight = DCMotor(pins_assignment[2], pins_assignment[3], correction_functions[1])
        self.lineSensors = LineSensors(pins_assignment[4], pins_assignment[5], pins_assignment[6], pins_assignment[7])
        self.tcount = 0
        #TODO: set inputs from other sensors

    def determine_situation(self, line_inputs) -> str:
        '''classify current situation: straight line, cross, T, left turn, right turn, reverse, no line'''
        for i, e in enumerate(line_inputs):
            line_inputs[i] = 0 if e < self.thresh else 1
        #go straight if front and not all 4
        if (line_inputs[0] == 1) and (not line_inputs == [1, 1, 1, 1]):
            situation = 'straight_line'

        #NOTE: for left and right turns, robot will make small corrections until situation changes, so can be used for getting back on course too.
        #turn left if left and rear only, or left only
        elif (line_inputs == [0, 1, 0, 1]):
            situation = "Tleft"
            
        elif (line_inputs == [0, 1, 0, 0]):
            situation = 'left_turn'

        #similarly turn right if right and rear only, or right only
        elif (line_inputs == [0, 0, 1, 1]):
            situation = "Tright"
            
        elif (line_inputs == [0, 0, 1, 0]):
            situation = 'right_turn'

        #all 4 then report cross. not used for now
        elif (line_inputs == [1, 1, 1, 1]):
            situation = 'cross'
        
        #T. not used for now. But could be used to stop in the future
        elif (line_inputs == [0, 1, 1, 1]):
            situation = 'T'
        
        #if rear only it means we've gone too far. so backtrack in the hopes of finding something
        elif (line_inputs == [0, 0, 0, 1]):
            situation = 'reverse'
        
        #all other situations imply something is wrong
        else:
            situation = 'no_line'
        
        #finally output the situation
        return situation

    def make_correction(self, sensor_data: list): #TODO
        '''based on situation, use motors to apply a correction'''
        
        radical_turn = False
        for v in sensor_data:
            if v > self.thresh:
                radical_turn = True
        print(radical_turn)
        if True or not radical_turn:
            #pid
            error = sensor_data[2] - sensor_data[1]
            self.motorLeft.forward(80 + 20*error)
            self.motorRight.forward(80 - 20*error)
        else:
            pass
            '''
            sit = self.determine_situation(sensor_data)
            if sit == 'straight_line' or sit == 'cross' or sit == 'Tleft' or sit == 'Tright':
                self.motorLeft.forward(70)
                self.motorRight.forward(70)
            elif sit == 'T':
                self.tcount += 1
                if self.tcount % 2 == 1:
                    self.motorLeft.forward(100)
                    self.motorRight.reverse(100)
                    sleep(1)
                else:
                    self.motorLeft.reverse(100)
                    self.motorRight.forwards(100)
                    sleep(1)
            elif sit == 'right_turn':
                self.motorLeft.forward(100)
                self.motorRight.reverse(100)
                sleep(1)
            elif sit == 'left_turn':
                self.motorLeft.reverse(100)
                self.motorRight.forward(100)
                sleep(1)
            elif sit == 'reverse':
                self.motorLeft.reverse(70)
                self.motorRight.reverse(70)
            else:
                print("panic")
            '''
