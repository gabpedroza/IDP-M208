class Junction:
    node_number = 0
    def __init__(self, shape):
        
        self.modes = {}
        if(shape == "T"):
            self.shape = {0: [1, 0], 1: [1, 1], 2: [0, 1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0, 0,0]
        elif shape == "L":
            self.shape = {0 : [1, 0], 1:[0, 1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0,0,0]
        else:
            self.shape = {0: [1,1], 1: [1,1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0,0,0]
        self.node_number = Junction.node_number
        Junction.node_number += 1
        self.connections = {}

    def connect(self, index_self, other, index_other):
        self.connections[index_self] = (other, index_other)
        other.connections[index_other] = (self, index_self)
class Plant:

    def init_nodes(self):
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
        for i in [1, 12]:
            self.nodes[i].modes["ground"] = [False,True,False,False]
        for i in [22, 2]:
            self.nodes[i].modes["ground"] = [False,False,False,False]
        for i in list(range(4, 9 + 1)) + list(range(15, 20 + 1)):
            self.nodes[i].modes["ground"] = [False,False,False,False]
        for i in [11,13]:
            self.nodes[i].modes["ground"] = [True,True,True,True]
        for i in [10, 14]:
            self.nodes[i].modes["ground"] = [False,False,False,False]
        self.nodes[21].modes["ground"] = [False,False,True, True]
        self.nodes[3].modes["ground"] = [True, False, False, True]
    
    def init_ground_connections(self):
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

    def __init__(self):
        self.init_nodes()
        self.init_ground_connections()
        self.init_ground_modes()
        #second floor connections