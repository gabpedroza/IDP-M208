# Software
## Algorithms
### General outline
The robot operates in 3 clearly distinct modes.
1. "ground": It circles around the ground floor of the arena, looking for boxes. It does so by checking with the left-hand side distance sensor.
2. "second: It goes back and forth in the second floor, looking for boxes. In this case, it has to use sensors on both sides.
3. Delivery (encapsulates the deprecated pickGround and pickSecond modes, as well as the going home): follows a breadth-first algorithm to go between two specified nodes. 

It starts on the ground mode, and momentarily switches to delivery mode on each detected box. After two boxes are picked up and delivered, it switches to second mode, and goes back to delivery whenever it finds a box. After finding the last two boxes, it delivers itself to the start area through the delivery mode. 
### Sensing lines
The robot averages out a set of line measurements to produce a list of values on which to act. White and black are hence defined through a threshold. This smoothes out possible small glitches in the sensors. 

The two middle sensors only care about PID (stright line following). The two external sensors only care about node detection. Node detection is a two-step process:
 1. If any external sensor detects something white, it records that. The node has not yet been detected.
 2. After a specified period of time since this first detection (currently 150ms), it checks again, with both sensors. The outcome of this measurement gives the output of node detection.

This is to ensure even a misaligned robot can detect a cross (+) pattern correctly.  
### PID
It's actually a poportional controller for following straight lines. It's executed whenever a node is not detected.
### Radical turn
A radical turn is the behaviour of the robot upon detecting a node. It doesn't necessarily involve a physical turn; it just means the robot turns off its PID mind and follows whatever is specified for that node in that mode, as descrbed in the modes dictionary. 
### Appendix: the BFS algorithm
A graph is a set of nodes connected by edges (which are, in our case, straight segments). The node picture of the arena naturally gives way to thinking of it as a graph.

Given two nodes in a graph, the problem of finding the best path between them, using edges as roads, is non-trivial. The breadth-first algorithm finds the path that minimises path length as computed by the number of nodes in it. It does so as follows, using the help of a queue (all nodes start with infinite distance):
1. Given a node $A$, check all of its neighbours $B_i$
2. If some node $B_j$ has infinite distance, update its distance as $d(B_j) = d(A) + 1$ and push it into the queue.
3. After all neighbouring nodes $B_j$ have been checked, take the first node in the queue to be $A$ and go back to step 1.

The algorithm is kickstarted by picking the starting node to be $A$ and setting its distance to be 0. It then proceeds until the queue is empty. One can picture it as a contagious process where nearer nodes are infected first; thus it minimises distances according to node count.

In order to build a path between $P$ and $Q$ with it, one runs BFS starting at $P$, thus getting a list of the distance of all nodes to $P$. Then one starts at $Q$ and traces back the path: given a node $K$ in the path, the previous node must have had distance $d(K) - 1$. Since $Q$ is in the path, this reconstructs the shortest path recursively. (Of course this need not be *the* unique shortest path. Several paths can have the overall, minimum distance).

Alternatively, simply trust the `Follower._bfs` method works and don't touch it.
## Class specifications
### Junction
The `Junction` class is in the `graph_model.py` file. It models the features of the arena as nodes. A feature can be understood as any line pattern which is not plainly straight.

Each `Junction` instance has four sides, numbered from 0 to 3. They are absolute values, i.e. independent of `Junction` or robot orientation. If one looks at the arena so that the home (start) square is in its upper side, then the numbers can be understood to mean, from 0 to 3, East, North, West, and South, respectively. 
#### Attributes
A `Junction` instance has attributes:
- `self.shape`: Can be one of `"L"`, `"T"`, and `"+"`. It is only used for visualisation purposes (e.g. in the `Plant` method `print`).

- `self.node_number`: a unique `int` identifying the node. In particular, `Plant.nodes[node_number]` indexes the node on the arena.

- `self.connections`: a dictionary of `int : tuple(Junction, int)`. It conveys the connections between nodes. `junctionA.connections[3]==(junctionB, 1)` means that `junctionA` has its side `3` connected to side `1` of `junctionB`.

- `self.modes`: a dictionary of lists with keys `"ground"`, `"pickGround"`, `"second"`, and `"pickSecond"`. Currently, the `"pick*"` modes are deprecated; the other modes are followed by the robot when hunting for boxes in the ground and second floor, respectively. For each mode, the list associated with its name is made of 4 entries, symbolising the behaviour of the robot when entering each one of the sides of the tile. For example, if the node has `mode["ground"]==["left", "front", "right", "backR"]`, then the robot is expected to turn left when entering side `0`, continue ahead when entering side `1`, turn right when entering side `2`, and do a 180 deg turn on its right when entering side `3`.
#### Constructor
The constructor takes a `shape` parameter, which can be `"T"`, `"L"`, or `"+"`, corresponding to the obvious types of line patterns.
#### `connect` method
Calling `junctA.connect(a, junctB, b)` connects node `junctA` to `junctB`, on the side `a` of the former and side `b` of the latter. Notice that it updates the `connections` dictionary of both `junctA` and `junctB` (i.e. it assumes the connection is bidirectional).

### Plant
The `Plant` class is in the `graph_model.py` file. Its instance represents the arena. 

#### Attributes 
- `self.nodes`: list of all the `Junction`s of the arena. Indexes are by node_number. 
- `self.boxes`: dictionary of `int : str` mapping node_number to the box colour associated with it. This is for testing and debugging only.
#### `print` method
This is for simulating the robot. It takes in (optionally) the current node of the robot as node_number, optionally its orientation, and an optional list of nodes. It then prints a picture of the arena with the current node and path highlighted.

#### `add_box` method
Adds a box with colour `colour` at node `node_number`. For debugging purposes only.

#### `init_nodes` metod
Creates all the `Junction` instances. The order of their creation is **critical** because that specifies the node_numbers. Changing a single line can potentially break everything. Additions should be done only in the end of the method, never in the middle. 

#### `init_MODE_connections` methods
Wires up the node connections for the nodes in the MODE floor. All connections are bidirectional, except for nodes 31 and 39, which are the `"T"` nodes at the end of the racks of the second floor. They have a ghost, uni-directional connection from their side 3 to side 3 of nodes 30 and 38, respectively. This is to make that odd 180 degree turn work seamlessly with the algorithms.

#### `init_MODE_modes` methods
Sets up the `mode` dictionary for each node involved in MODE. Notice that the second floor modes also involve the ground floor because the robot must be able to climb from the ground floor to the second floor after it's done with the former. They effectively specify the box-hunting path following.

#### Constructor
Calls all of the partial constructors above, except the `*pick*` constructors (hence they are deprecated).