class Junction:
    def __init__(self, shape):
        
        self.modes = {}
        if(shape == "T"):
            self.shape = {0: [1, 0], 1: [1, 1], 2: [0, 1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0, 0]
        elif shape == "L":
            self.shape = {0 : [1, 0], 1:[0, 1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0]
        else:
            self.shape = {0:, [1,1], 1: [1,1]}
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0]

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
        self.noes.append(Junction("L"))
        self.noes.append(Junction("T"))
        self.noes.append(Junction("L"))
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

    def init_ground_modes():
        for i in [1,2,4,5,6,7,8,9,12,15,16,17,18,19,20,22]:
            self.nodes[i].modes = [0,1,0]

        self.nodes[11].modes = [1,1]
        self.nodes[13].modes = [1,1]

        self.nodes[3].modes = [0,1,1]
        self.nodes[21].modes = [1,1,0]

        self.nodes[10].modes = [0,0]
        self.nodes[14].modes = [0,0]
    
    def init_ground_connections():
        self.nodes[1].connect(0, self.nodes[2], 2)
        self.nodes[1].connect(2, self.nodes[22], 0)

        self.nodes[2].connect(0, self.nodes[3], 1)

        for i in range(3, 9 + 1):
            self.nodes[i].connect(2, self.nodes[i+1], 0)

        self.nodes[10].connect(1, self.nodes[11], 0)
        self.nodes[11].connect(1, self.nodes[12], 0)

        self.nodes[12].connect(2, self.nodes[13], 0)

        self.nodes[13].connect(1, self.nodes[14], 0)
        self.nodes[14].connect(1, self.nodes[15], 0)
        for i in range(15, 20 + 1):
            self.nodes[i].connect(2, self.nodes[i+1], 0)

        self.nodes[21].connect(1, self.nodes(22), 2)

    def __init__(self):
        self.init_nodes()
        self.init_ground_connections()
        self.init_ground_modes()
        #second floor connections
        
    

    