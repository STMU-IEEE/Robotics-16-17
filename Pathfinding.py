from function import *
#
#    [0]A  [1]B  [2]C  [3]D  [4]E  [5]F  [6]G
#   +-----+-----+-----+-----+-----+-----+-----+
#[6]|     |     |     |     |     |     |     |
# 1 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[5]|     |     |     |     |     |     |     |
# 2 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[4]|     |     |     |     |     |     |     |
# 3 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[3]|     |     |     |     |     |     |     |
# 4 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[2]|     |     |     |     |     |     |     |
# 5 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[1]|     |     |     |     |     |     |     |
# 6 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[0]|START|     |     |     |     |     |     |
# 7 |  X  |     |     |     |     |     |     |
#   |HE RE|     |     |     |     |     |     |
#   +-----+-----+-----+-----+-----+-----+-----+

import numpy as np
# from heapq import *

blocked_vals = {-1}  # this is a list of the possible blocked values for pathfinding purposes
my_location = (0,0) # first val for vert, second for horiz (row, col)
default_path = np.array(
    [0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],
    [1,6],[1,5],[1,4],[1,3],[1,2],[1,1],[1,0],
    [2,0],[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],
    [3,6],[3,5],[3,4],[3,3],[3,2],[3,1],[3,0],
    [4,0],[4,1],[4,2],[4,3],[4,4],[4,5],[4,6],
    [5,6],[5,5],[5,4],[5,3],[5,2],[5,1],[5,0],
    [6,0],[6,1],[6,2],[6,3],[6,4],[6,5],[6,6]
)
my_path=default_path

world_map = np.full((7,7), 8, dtype=np.int)
# unexplored blocks will have a travel cost value of 8.
# this travel cost will be reduced to 1 when the robot explores that region.
flow_map = []

def follow(path, globalPath):

    while path:
        if my_location == path[0]:
            path = np.delete(path,0); # if we have reached the next location, remove it from the path.
        if world_map[my_location[0]][my_location[1]]<1:
            world_map[my_location[0]][my_location[1]]=1

        # run sensors and \
        get_sensors(my_location) # update surrounding nodes
        if world_map[path[0][0]][path[0][1]] in blocked_vals:
            path = np.delete(path,0); # if my next point is blocked, move on to the next point in the path.
        # update the map here
        flow_map = flowField(world_map, path[0])
        travel_direction = flow_map[my_location[0],my_location[1]]
        if travel_direction[0] > 0: # if we need to move north
            move_north()
        elif travel_direction[0] < 0: # if we need to move south
            move_south()
        elif travel_direction[1] > 0: # if we need to move west
            move_west()
        else:   # else move east
            move_east()

def you_are_here(): #for debug purposes
    view_map = world_map
    view_map[my_location[0]][my_location[1]] = 'X'
    print(view_map)

def dist(a, b):
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) **.5

def flowField(world, target):
    output_field = np.zeros((7,7,2), dtype=np.int)
    neighbor_dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    closed_set = set()
    parents = {}
    g_score = {start:0}
    open_set = set() # list of nodes to be explored

    open_set.add(target)


    while open_set:
        my_loc = open_set.pop(0)
        for i,j in neighbor_dirs:
            neighbor = my_loc[0] + i, my_loc[1] + j
            if 0 <= neighbor[0] < world.shape[0]:
                if 0 <= neighbor[1] <= world.shape[1]:
                    if world[neighbor[0]][neighbor[1]] not in blocked_vals:
                        open_set.add(neighbor)
                        g_score[neighbor] = g_score[my_loc] + world[neighbor[0]][neighbor[1]]
                    else: continue
                    g_score[neighbor] = -1
                else: continue
            else: continue



    return output_field
def move_north():
	move_y(1,1)
	return
def move_south():
	move_y(2,1)
	return
def move_east():
	move_x(1,1)
	return
def move_west():
	move_x(2,1)
	return
def get_sensors(location):
	block_direction = us_sensor()
	print(block_direction)
	current_block_identity = capacitor_block_identity()
	print(current_block_identity)
	#Ultrasonic function return values
	#0: no near by block
	# North 1000
	# South  100
	# East    10
	# West     1
	#Example of multiple blocks: North and South: #1100
	#Capacitor function return values
	#-1 -> Warning retake value
	#0-> tunnel
	#1-> dead_ends
	#2-> Insulation
	world_map[my_location[0]][my_location[1]] = current_block_identity

	if(block_direction[0] == 1):#North
		world_map[my_location[0]+1][my_location[1]] = -1;
	elif(block_direction[1] == 1):#South
		world_map[my_location[0]-1][my_location[1]] = -1;
	elif(block_direction[2] == 1):#East
		world_map[my_location[0]][my_location[1]+1] = -1;
	elif(block_direction[3] == 1):#West
		world_map[my_location[0]][my_location[1]-1] = -1;
	return
