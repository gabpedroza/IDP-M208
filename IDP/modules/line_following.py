'''Main module for line following logic'''
from modules.drive_motors import DCMotor, LinearActuator
from modules.line_sensors import LineSensors
from modules.graph_model import Plant
from modules.linear_actuator import LinearActuator
from modules.distance_sensors import FrontDistance
from modules.colour import ColourSensor
from machine import SoftI2C, I2C, Pin
from utime import sleep, ticks_ms, sleep_ms
class Follower:
    '''Figure out the situation the robot is in at a single time step, and apply correction. '''
    def __init__(self, pins_assignment : list, thresh= 0.5, correction_functions = [lambda x: x, lambda x: x]):
        '''set variables on initialization. Pin ordering: motorLeft x 2, motorRight x2, (far left,left,right, far right) TTL, actuator dir, actuator PWM, front dist sda, front dist scl, colour sda, colour scl, colour enable
            correction_functions order: left, right'''
        #ultrasound gp27, adc1; button gp25
        #store inputs from the line sensors. These will already be processed to be binary (1 or 0). Format: front, left, right, rear
        self.thresh = thresh
        self.motorLeft = DCMotor(pins_assignment[0], pins_assignment[1], correction_functions[0])
        self.motorRight = DCMotor(pins_assignment[2], pins_assignment[3], correction_functions[1])
        self.lineSensors = LineSensors(pins_assignment[4], pins_assignment[5], pins_assignment[6], pins_assignment[7])
        self.linearActuator = LinearActuator(pins_assignment[8], pins_assignment[9])
        self.frontDistance = FrontDistance(SoftI2C(sda=pins_assignment[10], scl=pins_assignment[11], freq=100000))
        
        #colour sensor activation
        enabler = Pin(pins_assignment[14], Pin.OUT)
        enabler.high()
        sleep_ms(3)
        self.colourSensor = ColourSensor(I2C(0, sda=Pin(pins_assignment[12]), scl=Pin(pins_assignment[13]), freq=400000), enable_pin=pins_assignment[14])
        enabler.low()

        self.turn_timer = [0,0,0,0]
        self.waiting= 0
        self.skip_time = 0.2
        self.node = 1
        self.orientation = 1
        self.plant = Plant()
        self.landmark_map = {"red":3, "yellow":2, "green":22, "blue":21, "home":1}
        #TODO: set inputs from other sensors

    def detect_radical_turn(self, sensor_data):
        """Detects whether a node has been found
           Takes in sensor_data [far left, left, right, far right]
           Returns list[bool] representing whether sensor [left, right] has seen a radical (node-like) turn
        """
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
            """It's actually a proportional controller. """
            error = sensor_data[2] - sensor_data[1]
            self.motorLeft.forward(70 + 30*error)
            self.motorRight.forward(70 - 30*error)

    def algorithm_ground(self, sensor_data):
        '''
        Takes in sensor_data and decides what to do based on the ground mode algorithm and the current state of the robot.
        Most nodes behaviour can be inferred from their modes["ground"] list, which often disallows any turns
        Some other nodes have obvious turning policies hadled by a simple if/elif couple
        A few are T junctions and the robot must simply know what to do. These are listed on the turns dictionary with their behaviour.
        '''
        
        radical_turn = self.detect_radical_turn(sensor_data)

        if not radical_turn[0] and not radical_turn[1]:
            self.pid(sensor_data)
        else:
            self._turn(self.plant.nodes[self.node].modes["ground"][self.orientation])

            #The robot is basically performing a depth-first search. After entering a node, it updates itself to match that node
            #NB the orientation was updated in the _turn function
            next_node = self.plant.nodes[self.node].connections[self.orientation]
            self.node, self.orientation = next_node[0].node_number, next_node[1]

    def algorithm_second(self, sensor_data):
        '''
        Takes in sensor_data and decides what to do based on the ground mode algorithm and the current state of the robot.
        Most nodes behaviour can be inferred from their modes["ground"] list, which often disallows any turns
        Some other nodes have obvious turning policies hadled by a simple if/elif couple
        A few are T junctions and the robot must simply know what to do. These are listed on the turns dictionary with their behaviour.
        '''
        
        radical_turn = self.detect_radical_turn(sensor_data)

        if not radical_turn[0] and not radical_turn[1]:
            self.pid(sensor_data)
        else:
            self._turn(self.plant.nodes[self.node].modes["second"][self.orientation])

            #The robot is basically performing a depth-first search. After entering a node, it updates itself to match that node
            #NB the orientation was updated in the _turn function
            next_node = self.plant.nodes[self.node].connections[self.orientation]
            self.node, self.orientation = next_node[0].node_number, next_node[1]

    def _bfs(self, node_start, node_end):
        """
        Given a start node and an end node, returns the path between them that minimises node count, as a list of (node, orientation)
        """
        #simple BFS
        distances = {}
        distances[node_start] = 0
        to_visit = [self.plant.nodes[node_start]]
        while len(to_visit) > 0:
            current_node = to_visit[0]
            to_visit = to_visit[1:]
            for n, ori in current_node.connections.values():
                if n.node_number not in distances.keys():
                    distances[n.node_number] = distances[current_node.node_number] + 1
                    to_visit.append(n)
        #backtracks the BFS starting from the end node. The previous node will be the one with -1 the distance of the current node
        end_distance = distances[node_end]
        path = [node_end]
        c_n = self.plant.nodes[node_end]
        while c_n.node_number != node_start:
            for my_ori, pairs in c_n.connections.items():
                n, ori = pairs
                if distances[n.node_number] == distances[c_n.node_number] - 1:
                    path.append((n, ori))
                    c_n = n
                    break
        path[0] = (self.plant.nodes[node_end], path[1][0].connections[path[1][1]][1])
        return path[::-1] #since we built the path by tracing back distances, the list is in the reverse order
    
    def pick_ground_box(self):
        """What the robot does when it has identified a box and needs to deliver it. and then return to path.
        Starts from when the box was identified (so the first thing is turn left) and ends having picked up the box and turned around"""
        #turn left
        self._turn("left") #we can make this more modular later to account for 2nd floor right turns
        #easiest to just extend the fork here
        self.linearActuator.extend_fork()

        arrived = False
        
        #until we have arrived, keep following the line and checking distance
        while not arrived:
            #get data from line sensors and do pid for line following
            for i in range(10):
                self.lineSensors.get_new_values()
            avg = self.lineSensors.get_averages()
            self.pid(avg)

            #check distance for arrival
            distance = self.frontDistance.get_distance()
            if distance < self.frontDistance.arrival_distance:
                arrived = True #on next loop the while loop will be bypassed

        #having arrived, we are 5 mm away (must check if this is enough). we need to be 3mm away. so walk a tiny bit more
        self.walk(0.2) #try 0.2s of walking
        self.walk(0.001, 0) #must stop motors

        #activate colour sensor
        self.colourSensor.enable()
        #determine colour, save this value in the instance for use in other functions
        self.box_colour = self.colourSensor.get_colour() #this takes a second (literally 1 second)
        #deactivate colour sensor immediately after use, as per specifications
        self.colourSensor.disable()

        #pick up box using linear actuator (just need to retract fork)
        self.linearActuator.retract_fork()

        #reverse a bit then turn 180 degrees. Now we're done and line following takes over
        self.walk(1, -100)
        self._rotate(deg=180)

        #if needed, we can do pid line following here until we get to the junction we started at. @gabriel depends on where deliver_ground_box takes over
        

    def deliver_box(self):
        '''Delivers box and returns to the same spot, oriented with the main line.'''
        #follow path to destination
        goal_node = self.landmark_map[self.box_colour]
        path = self._bfs(self.node, goal_node)
        while(self.orientation != path[0][1]):
            self._rotate()
        for n, o in path[1:]:
            radical_turn = [0,0]
            while(not radical_turn[0] and not radical_turn[1]):
                for i in range(10):
                    self.lineSensors.get_new_values()
                avg = self.lineSensors.get_averages()
                radical_turn = self.detect_radical_turn(avg)
                if not radical_turn[0] and not radical_turn[1]:
                    self.pid(avg)
                else:
                    if o == (self.orientation+1)%4:
                        self._turn("right")
                    elif o==(self.orientation-1)%4:
                        self._turn("left")
                    else:
                        pass
                    self.node = n.node_number
                    self.orientation = o

        #is in the node that leads to the colour
        self.walk(1.5)
        #drop off the box
        self.linearActuator.extend_fork()
        self.walk(0.5, -100)
        self.linearActuator.retract_fork()
        self.walk(1, -100)
        #time to go back

        while(self.orientation != path[-1][1]):
            self._rotate()
        for n, o in path[::-1][1:]:
            my_orientation = (o+2)%4 #the storage is beginning *-> *-> .... * end. Hence to know the reverse direction I must now the orientation
            #at the other end of the arrow. 
            radical_turn = [0,0]
            while(not radical_turn[0] and not radical_turn[1]):
                for i in range(10):
                    self.lineSensors.get_new_values()
                avg = self.lineSensors.get_averages()
                radical_turn = self.detect_radical_turn(avg)
                if not radical_turn[0] and not radical_turn[1]:
                    self.pid(avg)
                else:
                    if my_orientation == (self.orientation+1)%4:
                        self._turn("right")
                    elif my_orientation==(self.orientation-1)%4:
                        self._turn("left")
                    else:
                        pass
                    self.node = n.node_number
                    self.orientation = my_orientation
            #theoretically should be back now

    def _rotate(self, direction="right", deg=90):
        if direction == "left":
            self.motorLeft.reverse(100)
            self.motorRight.forward(100)
            sleep(0.6*deg/90)
            self.orientation = (self.orientation-deg/90)%4
        elif direction == "right":
            self.motorLeft.forward(100)
            self.motorRight.reverse(100)
            sleep(0.6*deg/90)
            self.orientation = (self.orientation+deg/90)%4
        self.walk(0.001,0)
    
    def _turn(self, direction, speed = 100, delay1 = 0.6, delay2 = 0.5):
        '''turns the robot 90deg. Direction is either "left" or "right".
            delay1 is the time of the actual turn, delay2 is the move time it moves front before turning'''
        if direction == "left" or direction == "right":
            pass
        if(direction == "left"):
            self.orientation = (self.orientation-1)%4
            self.motorRight.forward(100)
            self.motorLeft.forward(20)
            sleep(1.6)
        elif(direction == "right"):
            self.orientation = (self.orientation+1)%4
            self.motorLeft.forward(100)
            self.motorRight.forward(30)
            sleep(1.5)
        elif(direction == "backR"):
            self._rotate("right", 180)
            self.orientation = (self.orientation+2)%4
            self.node -= 1
        elif direction == "backL":
            self._rotate("left", 180)
            self.orientation = (self.orientation+2)%4
            #self.node -= 1
        else:
            self.orientation = (self.orientation + 2)%4

    def walk(self, delay, speed = 100):
        '''Moves forwards (speed > 0) or backwards (speed < 0). Can stop with speed == 0'''
        if(speed > 0):
            self.motorLeft.forward(speed)
            self.motorRight.forward(speed)
        else:
            self.motorLeft.reverse(speed)
            self.motorRight.reverse(speed)
        sleep(delay)
