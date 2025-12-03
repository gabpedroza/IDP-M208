from graph_model import Plant
class virtualFollower:
    '''Figure out the situation the robot is in at a single time step, and apply correction. '''
    def __init__(self, thresh= 0.5):
        '''set variables on initialization. Pin ordering: motorLeft x 2, motorRight x2, (far left,left,right, far right) TTL, actuator dir, actuator PWM, front dist sda, front dist scl, colour sda, colour scl, colour enable
            correction_functions order: left, right'''

        #store inputs from the line sensors. These will already be processed to be binary (1 or 0). Format: front, left, right, rear
        self.thresh = thresh

        self.turn_timer = [0,0,0,0]
        self.waiting= 0
        self.skip_time = 0.2
        self.node = 1
        self.orientation = 1
        self.plant = Plant()
        self.landmark_map = {"red":3, "yellow":2, "green":22, "blue":21, "home":1}
        self.box_count = 0
        self.box_colour = "red"
        #TODO: set inputs from other sensors

    def detect_radical_turn(self, sensor_data=[]):
        """Detects whether a node has been found
           Takes in sensor_data [far left, left, right, far right]
           Returns list[bool] representing whether sensor [left, right] has seen a radical (node-like) turn
        """
        return [True, True]

    def pid(self, sensor_data=[]):
        """It's actually a proportional controller. """
        print("pid")

    def hunt_box(self, sensor_data, mode):
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
            self._turn(self.plant.nodes[self.node].modes[mode][self.orientation])

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
            print(f"visited {current_node.node_number}")
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
                    path.append((n, (ori+2)%4))
                    c_n = n
                    print(f"im in {c_n.node_number}")
                    break
        path[0] = (self.plant.nodes[node_end], path[1][0].connections[path[1][1]][1])
        print("ill return")
        return path[::-1] #since we built the path by tracing back distances, the list is in the reverse order
    
    def pick_ground_box(self, colour="red"):
        self.box_colour = colour
        self.box_count += 1
        return
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
        self.plant.print(self.node, path=path)
        while(self.orientation != path[0][1]):
            self._rotate()
        for n, o in path[1:]:
            radical_turn = [0,0]
            while(not radical_turn[0] and not radical_turn[1]):
                #for i in range(10):
                #    self.lineSensors.get_new_values()
                #avg = self.lineSensors.get_averages()
                radical_turn = self.detect_radical_turn()
                if not radical_turn[0] and not radical_turn[1]:
                    self.pid()
                else:
                    if o == (self.orientation+1)%4:
                        self._turn("right")
                    elif o==(self.orientation-1)%4:
                        self._turn("left")
                    else:
                        pass
                    self.node = n.node_number
                    self.orientation = o
                    self.plant.print(self.node, path=path)

        #is in the node that leads to the colour
        self.walk(1.5)
        #drop off the box
        #self.linearActuator.extend_fork()
        self.walk(0.5, -100)
        #self.linearActuator.retract_fork()
        self.walk(1, -100)
        #time to go back
        print(f"box_count = {self.box_count}")
        if self.box_count != 4:
            while(self.orientation != path[-1][1]):
                self._rotate()
            for n, o in path[::-1][1:]:
                my_orientation = (o+2)%4 #the storage is beginning *-> *-> .... * end. Hence to know the reverse direction I must now the orientation
                #at the other end of the arrow. 
                radical_turn = [0,0]
                while(not radical_turn[0] and not radical_turn[1]):
                    for i in range(10):
                        pass #self.lineSensors.get_new_values()
                    #avg = self.lineSensors.get_averages()
                    radical_turn = self.detect_radical_turn()
                    if not radical_turn[0] and not radical_turn[1]:
                        self.pid()
                    else:
                        if my_orientation == (self.orientation+1)%4:
                            self._turn("right")
                        elif my_orientation==(self.orientation-1)%4:
                            self._turn("left")
                        else:
                            pass
                        self.node = n.node_number
                        self.orientation = my_orientation
                        self.plant.print(self.node, path=path)
                #theoretically should be back now
            self.orientation = (self.orientation + 2)%4
            print(f"{self.orientation}, {self.node}")
        else:
            self.go_home()
    def go_home(self):
        goal_node = self.landmark_map["home"]
        path = self._bfs(self.node, goal_node)
        self.plant.print(self.node, path=path)
        while(self.orientation != path[0][1]):
            self._rotate()
        for n, o in path[1:]:
            radical_turn = [0,0]
            while(not radical_turn[0] and not radical_turn[1]):
                #for i in range(10):
                #    self.lineSensors.get_new_values()
                #avg = self.lineSensors.get_averages()
                radical_turn = self.detect_radical_turn()
                if not radical_turn[0] and not radical_turn[1]:
                    self.pid()
                else:
                    if o == (self.orientation+1)%4:
                        self._turn("right")
                    elif o==(self.orientation-1)%4:
                        self._turn("left")
                    else:
                        pass
                    self.node = n.node_number
                    self.orientation = o
                    self.plant.print(self.node, path=path)
        print("DONE!!!!")
    def _rotate(self, direction="right", deg=90):
        if direction == "left":
            self.motorLeft.reverse(100)
            self.motorRight.forward(100)
            print(f"rotating left by {deg}")
            self.orientation = (self.orientation-deg/90)%4
        elif direction == "right":
            print(f"rotating right by {deg}")
            self.orientation = (self.orientation+deg/90)%4
        self.walk(0.001,0)
    
    def _turn(self, direction, speed = 100, delay1 = 0.6, delay2 = 0.5):
        '''turns the robot 90deg. Direction is either "left" or "right".
            delay1 is the time of the actual turn, delay2 is the move time it moves front before turning'''
        if direction == "left" or direction == "right":
            pass
        if(direction == "left"):
            self.orientation = (self.orientation-1)%4
            #self.motorRight.forward(100)
            #self.motorLeft.forward(20)
            #sleep(1.6)
        elif(direction == "right"):
            self.orientation = (self.orientation+1)%4
            #self.motorLeft.forward(100)
            #self.motorRight.forward(30)
            #sleep(1.5)
        elif(direction == "backR"):
            #self._rotate("right", 180)
            self.orientation = (self.orientation+2)%4
            
        elif direction == "backL":
            #self._rotate("left", 180)
            self.orientation = (self.orientation+2)%4
            
        else:
            self.orientation = (self.orientation + 2)%4

    def walk(self, delay, speed = 100):
        '''Moves forwards (speed > 0) or backwards (speed < 0). Can stop with speed == 0'''
        print("walking")
    
print("hey! this is a simulation!")
virtualRobot = virtualFollower()
virtualRobot.plant.add_box(5, "red")
virtualRobot.plant.add_box(16, "yellow")
virtualRobot.plant.add_box(25, "blue")
virtualRobot.plant.add_box(37, "green")                                  
virtualRobot.node = 1
virtualRobot.orientation = 1
box_count = 0
for i in range(99999):
    if(virtualRobot.node in virtualRobot.plant.boxes.keys()):
        virtualRobot.pick_ground_box(virtualRobot.plant.boxes[virtualRobot.node])
        virtualRobot.deliver_box()
        del virtualRobot.plant.boxes[virtualRobot.node]
    if virtualRobot.box_count <= 1:
        virtualRobot.hunt_box([], "ground")
    elif virtualRobot.box_count <= 3:
        virtualRobot.hunt_box([], "second")        
    else:
        while True:
            pass
    virtualRobot.plant.print(node_number=virtualRobot.node)


