'''Main module for line following logic'''

class Follower:
    '''figure out the situation the robot is in at a single time step, and apply correction'''
    def __init__(self, line_inputs: list):
        '''set variables on initialization'''

        #store inputs from the line sensors. These will already be processed to be binary (1 or 0). Format: front, left, right, rear
        self.line_inputs = line_inputs

        #TODO: set inputs from other sensors

    def determine_situation(self) -> str:
        '''classify current situation: straight line, cross, T, left turn, right turn, reverse, no line'''

        #go straight if front and not all 4
        if (self.line_inputs[0] == 1) and (not self.line_inputs == [1, 1, 1, 1]):
            situation = 'straight_line'

        #NOTE: for left and right turns, robot will make small corrections until situation changes, so can be used for getting back on course too.
        #turn left if left and rear only, or left only
        elif (self.line_inputs == [0, 1, 0, 1]) or (self.line_inputs == [0, 1, 0, 0]):
            situation = 'left_turn'

        #similarly turn right if right and rear only, or right only
        elif (self.line_inputs == [0, 0, 1, 1]) or (self.line_inputs == [0, 0, 1, 0]):
            situation = 'right_turn'

        #all 4 then report cross. not used for now
        elif (self.line_inputs == [1, 1, 1, 1]):
            situation = 'cross'
        
        #T. not used for now. But could be used to stop in the future
        elif (self.line_inputs == [0, 1, 1, 1]):
            situation = 'T'
        
        #if rear only it means we've gone too far. so backtrack in the hopes of finding something
        elif (self.line_inputs == [0, 0, 0, 1]):
            situation = 'reverse'
        
        #all other situations imply something is wrong
        else:
            situation = 'no_line'
        
        #finally output the situation
        return situation

    def make_correction(self, situation: str): #TODO
        '''based on situation, use motors to apply a correction'''