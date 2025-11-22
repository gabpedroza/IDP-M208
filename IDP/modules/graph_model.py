import sys
if sys.implementation.name == "cpython":
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import matplotlib.patches as patches
    debug_mode = True
else:
    debug_mode = False


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
            self.shape = "T"
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0, 0,0]
        elif shape == "L":
            self.shape = "L"
            for mode in ["ground", "pickGround", "second", "pickSecond"]:
                self.modes[mode] = [0, 0,0,0]
        elif shape == "+":
            self.shape = "+"
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
    def print(self, node_number = -1, orientation = -1, path=[]): 
        if debug_mode:
            grid = [
                [3,  2, 1,  22, 21],
                [0, 24, 23, 32,  0],
                [4,  25, 0, 33, 20],
                [5,  26, 0, 34, 19],
                [6,  27, 0, 35, 18],
                [7,  28, 0, 36, 17],
                [8,  29, 0, 37, 16],
                [9,  30, 0, 38, 15],
                [10, 31, 0, 39, 14],
                [11, 0, 12,  0, 13],
            ]
            mapping = {0:0, -1:1}
            for i in range(1, 40):
                mapping[i] = 2
            n_grid = [[mapping[i] for i in c] for c in grid]
            colour_map = ListedColormap(["black", "red", "grey"])

            fig, ax = plt.subplots()
            im = ax.imshow(n_grid, cmap=colour_map, vmin=0, vmax=2)
            ax.set_xticks([])
            ax.set_yticks([])
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if(grid[r][c] not in [0, -1]):
                        rotation = 0
                        if grid[r][c] in [2,1,22,12,32, 31, 39]:
                            rotation = 180
                        elif grid[r][c] in [3,4,5,6,7,8,9,33,34,35,36,37,38, 13]:
                            rotation = 90
                        elif grid[r][c] in [21,20,19,18,17,16,15,25,26,27,28,39,30, 24]:
                            rotation = -90
                        
                        ax.text(
                            c, r,
                            self.nodes[grid[r][c]].shape,
                            ha="center",
                            va="center",
                            rotation_mode="anchor",
                            color="black",
                            rotation=rotation
                        )
            for n, o in path:
                for i in range(len(grid)):
                    for j in range(len(grid[0])):
                        if grid[i][j] == n.node_number:  
                            highlight = patches.Rectangle(
                            (j-0.5, i-0.5),
                            1, 1,
                            linewidth=2,
                            edgecolor="yellow",
                            facecolor="none"
                            )
                            ax.add_patch(highlight)
            if(node_number == -1 and orientation == -1):
                pass
            else:
                for i in range(len(grid)):
                    for j in range(len(grid[0])):
                        if grid[i][j] == node_number:  
                            highlight = patches.Rectangle(
                            (j-0.5, i-0.5),
                            1, 1,
                            linewidth=2,
                            edgecolor="lime",
                            facecolor="none"
                            )
                            ax.add_patch(highlight)
            plt.show()
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
        self.nodes[node_end].modes["pickGround"] = ["right", "front", "left", "front"]

    def __init__(self):
        '''constructs the arena'''
        self.init_nodes()
        self.init_ground_connections()
        self.init_ground_modes()
        #second floor connections