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
def pathfinding_init():
    world_size = 7
    #TODO
    #blocked_vals = {-1}
    blocked_vals = np.array([-1])  # this is a list of the possible blocked values for default_Pathfinding purposes
    my_location = (0,0) # first val for vert, second for horiz (row, col)
    default_Path = np.array([
        [0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],
        [1,6],[1,5],[1,4],[1,3],[1,2],[1,1],[1,0],
        [2,0],[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],
        [3,6],[3,5],[3,4],[3,3],[3,2],[3,1],[3,0],
        [4,0],[4,1],[4,2],[4,3],[4,4],[4,5],[4,6],
        [5,6],[5,5],[5,4],[5,3],[5,2],[5,1],[5,0],
        [6,0],[6,1],[6,2],[6,3],[6,4],[6,5],[6,6]])

    world_map = np.full((world_size,world_size), 8, dtype=np.int)
    # unexplored blocks will have a travel cost value of 8.
    # this travel cost will be reduced to 1 when the robot explores that region.
    flow_map = []

    #Eduardo's Function Variables
    pos_direction = 0
    neg_direction = 0


def follow():


    while len(default_Path) > 0:
        if np.all(my_location == default_Path[0]):
            default_Path = np.delete(default_Path,0) # if we have reached the next location, remove it from the default_Path.

        if world_map[my_location[0]][my_location[1]]<1: #If we are above a obstacle, mark as non-obstacle
            world_map[my_location[0]][my_location[1]]=1

        # run sensors and \
        #TODO
		#error inside if statement
        get_sensors(my_location) # update surrounding nodes

        if int(world_map[default_Path[0][0]][default_Path[0][1]]) in blocked_vals:
            default_Path = np.delete(default_Path,0) # if my next point is blocked, move on to the next point in the default_Path.

        # update the map here
        #TODO LATER
        #When actually competing change function
        #to lightmatrix_update_simple
        lightmatrix_update(path[0][1],path[0][0], \
        world_map[my_location[0]][my_location[1]])


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
    #TODO
    #Start is not defined, assuming start is meant to be equal zero
    start = 0
    g_score = {start:0}
    open_set = set() # list of nodes to be explored

    open_set.add(target)


    while len(open_set) > 0:
        #TODO
        #open_set.pop should not have an argument
        #my_loc = open_set.pop(0), only found on web openset.pop()
        #openset.pop() is not defined
        my_loc = open_set.pop()
        for i,j in neighbor_dirs:
            #TODO
			#my_loc is a scalar variable and does not take index
            #Assuming my_loc was meant to say my_location
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
        for y in range(0,world_size):
            for x in range(0,world_size):
                if y == world_size-1:
                    y_dir = min(g_score[(y-1,x)]-g_score[(y,x)],0)
                elif y == 0:
                    #TODO
                    #y_dir = max(g_score[(y,x)]-g_score[(y+1,x)],0) ---> KeyError: (0, 0)

                    y_dir = max(g_score[(y,x)]-g_score[(y+1,x)],0)
                else:
                    y_dir = g_score[(y-1,x)]-g_score[(y+1,x)]

                if(y_dir != 0):
                    y_dir = y_dir/abs(y_dir) # normalize the vector.

                if (x == world_size-1) or (world_map[y][x+1] in blocked_vals):
                    x_dir = min(g_score[(y,x-1)]-g_score[(y,x)],0)
                elif x == 0 or world_map[y][x-1] in blocked_vals:
                    x_dir = max(g_score[(y,x)]-g_score[(y,x+1)],0)
                else:
                    x_dir = g_score[(y,x-1)]-g_score[(y,x+1)]

                if(x_dir != 0):
                    x_dir = x_dir/abs(x_dir) # normalize the vector.
                output_field[y][x]=(y_dir,x_dir)

    return output_field

def move_north():
    move_y(pos_direction)
    return
def move_south():
    move_y(neg_direction)
    return
def move_east():
    move_x(pos_direction)
    return
def move_west():
    move_x(pos_direction)
    return
def get_sensors(location):
    block_direction = us_sensor()
    print(block_direction)
    current_block_array = capacitor_block_multiple(3)

    print("List Received from Function:")
    print(current_block_array)
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
    max_index = current_block_array.index(max(current_block_array))
    print("max_index: {A}".format(A = max_index))
    world_map[my_location[0]][my_location[1]] = max_index

    if(block_direction[0] == 1):#North
        world_map[my_location[0]+1][my_location[1]] = -1
    elif(block_direction[1] == 1):#South
        world_map[my_location[0]-1][my_location[1]] = -1
    elif(block_direction[2] == 1):#East
        world_map[my_location[0]][my_location[1]+1] = -1
    elif(block_direction[3] == 1):#West
        world_map[my_location[0]][my_location[1]-1] = -1
    return
"""
follow(default_path, world_map)
print("Path Completed!")
exit()
"""
