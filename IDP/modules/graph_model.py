import math 


class Junction:
    '''Class representing line patterns which are not straight. 
       Attributes: 
           -modes: dict[str] : list[bool] gives the different turning patterns for each node mode. str can be "ground", "pickGround", "second", or "pickSecond". The index of the list
           is the orientation, cf. bellow. They are to be interpreted as the robot entering the node at that index.
           -node_number: an absolute number (int) identifying the node
           -connections: dict[int] : tuple(Junction, int) gives the edges between the node and its neighbour. The ints are the number at the ends of the edge, following this pattern:
                                      1
                                    2_|_0
                                      |
                                      3
                where the north side is the side with the starting box. The first int is on the self node, and the second on the other node
    '''
    node_number = 0
    def __init__(self, shape):
        """Initialises a node. 
            Shape 'T', 'L', or '+' representing the three junction types
            It can also be 'B' representing a box delivery place"""

        self.modes = {}
        if(shape == "T"):
            self.shape = {0: [1, 0], 1: [1, 1], 2: [0, 1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0, 0,0]
        elif shape == "L":
            self.shape = {0 : [1, 0], 1:[0, 1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0,0,0]
        elif shape == "+":
            self.shape = {0: [1,1], 1: [1,1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0,0,0]
        else:
            self.shape = {}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0,0,0]
        self.node_number = Junction.node_number
        Junction.node_number += 1
        self.connections = {}

    def connect(self, index_self, other, index_other):
        '''Connects self node to node other, from orientation named index_self to orientation named index_other'''
        self.connections[index_self] = (other, index_other)
        other.connections[index_other] = (self, index_self)
class Plant:
    '''This is a class representing the map.
    Attributes:
        -nodes: list is simply the list of all nodes in the arena. Their index is their node_number. Node 0 is a dummy node.'''

    def init_nodes(self):
        '''Creates all the arena nodes. NB. they are floating in space at this stage'''
        self.nodes = [Junction("T")] #dummy node
        for i in range(9):
            self.nodes.append(Junction("T"))
        self.nodes.append(Junction("+"))
        self.nodes.append(Junction("L"))
        self.nodes.append(Junction("T"))
        self.nodes.append(Junction("L"))
        self.nodes.append(Junction("+"))
        for i in range(8):
            self.nodes.append(Junction("T"))
        self.nodes.append(Junction("T"))
        self.nodes.append(Junction("L"))
        for i in range(7):
            self.nodes.append(Junction("T"))
        self.nodes.append(Junction("L"))
        for i in range(7):
            self.nodes.append(Junction("T"))

    def init_ground_modes(self):
        '''Initialises the modes for the nodes when the robot is in ground mode'''
        for i in [1, 12]:
            self.nodes[i].modes["ground"] = ["front","right","front","front"]
        for i in [22, 2]:
            self.nodes[i].modes["ground"] = ["front","right","front","front"]
        for i in list(range(4, 9 + 1)) + list(range(15, 20 + 1)):
            self.nodes[i].modes["ground"] = ["front","front","front","front"]

        self.nodes[11].modes["ground"] = ["right","left","front","front"]
        self.nodes[13].modes["ground"] = ["front","right","left","front"]

        for i in [10, 14]:
            self.nodes[i].modes["ground"] = ["front","front","front","front"]

        self.nodes[21].modes["ground"] = ["front","front","right","left"]
        self.nodes[3].modes["ground"] = ["left","front","front","right"]
    
    def init_ground_connections(self):
        '''Connects all the nodes involved in the ground and pickGround modes'''
        self.nodes[1].connect(2, self.nodes[2], 0)
        self.nodes[1].connect(0, self.nodes[22], 2)

        self.nodes[2].connect(2, self.nodes[3], 0)

        for i in range(3, 9 + 1):
            self.nodes[i].connect(3, self.nodes[i+1], 1)

        self.nodes[10].connect(3, self.nodes[11], 1)
        self.nodes[11].connect(0, self.nodes[12], 2)

        self.nodes[12].connect(0, self.nodes[13], 2)

        self.nodes[13].connect(1, self.nodes[14], 3)
        self.nodes[14].connect(1, self.nodes[15], 3)
        for i in range(15, 20 + 1):
            self.nodes[i].connect(1, self.nodes[i+1], 3)

        self.nodes[21].connect(2, self.nodes[22], 0)

    def init_pickgGround_modes(self, node_start, node_end):
        self.init_ground_modes()
        for i in range(1, 22 + 1):
            self.nodes[i].modes["pickGround"] = self.nodes[i].modes["ground"]
        self.nodes[node_start].modes["pickGround"] = ["front", "front", "front", "front"]
        self.nodes[node_end].connections[3][0].modes["pickGround"] = ["right", "front", "left", "front"]
        
    def __init__(self):
        '''constructs the arena'''
        self.init_nodes()
        self.init_ground_connections()
        self.init_ground_modes()
        #second floor connections