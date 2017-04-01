from function import *
from senseHat import *
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

default_path = [
[0,1],
[0,2],
[0,3],
[0,4],
[0,5],
[0,6],
[1,6],
[1,5],
[1,4],
[1,3],
[1,2],
[1,1],
[1,0],
[2,0],        
[2,1],
[2,2],
[2,3],
[2,4],
[2,5],
[2,6],
[3,6],
[3,5],
[3,4],
[3,3],
[3,2],
[3,1],
[3,0],
[4,0],
[4,1],
[4,2],
[4,3],
[4,4],
[4,5],
[4,6],
[5,6],
[5,5],
[5,4],
[5,3],
[5,2],
[5,1],
[5,0],
[6,0],
[6,1],
[6,2],
[6,3],
[6,4],
[6,5],
[6,6],
[0,0]]

#Eduardo's Function Variables
pos_direction = 0
neg_direction = 1
block_direction = [0,0,0,0]

Y = 1
X = 0

obstacle = 1
obstacle_present = -1

current_location = [0,0]
target_location = [0,0]
max_capacitor_index = 0

NORTH = 0
SOUTH = 1
EAST = 2
WEST = 3

move_direction = [0,0]
target_location_is_safe = 0
target_location_obstacle = 0
yes = 1
no = 0

world_map = [[8,8,8,8,8,8,8],
             [8,8,8,8,8,8,8],
             [8,8,8,8,8,8,8],
             [8,8,8,8,8,8,8],
             [8,8,8,8,8,8,8],
             [8,8,8,8,8,8,8],
             [8,8,8,8,8,8,8]]
wire = 0
dead_end = 1
insulation = 2

"""
for i in range(len(world_map)):
	for j in range(len(world_map[i])):
		world_map[i][j] = 8
"""
print (world_map)



def scan_field():
    global target_location
    while len(default_path) > 0:
        target_location = default_path[0]
        print("Target Location:\t", end = '')
        print(target_location, end = '')
        print("\tCurrent Location:\t", end = '')
        print(current_location)
        get_sensor()
        display_capacitor_reading()
        mark_obstacle()
        check_target_location()
        if(target_location_obstacle == yes):
            remove_target_block()
            continue
        list_of_movement()
        make_movement()
        remove_target_block()

def mark_obstacle():
    global world_map
    print("Entering mark_obstacle")
    for orientation in range(len(block_direction)):
        if(block_direction[orientation] == obstacle):
            #Orientation: 
            #0 --- North
            #1 --- South
            #2 --- East
            #3 --- West
            if(orientation == NORTH):
                 world_map[current_location[X]][current_location[Y] + 1] = obstacle_present
            if(orientation == SOUTH):
                 world_map[current_location[X]][current_location[Y] - 1] = obstacle_present
            if(orientation == EAST):
                 world_map[current_location[X] + 1][current_location[Y]] = obstacle_present
            if(orientation == WEST):
                 world_map[current_location[X] - 1][current_location[Y]] = obstacle_present
    return
        
def check_target_location():
    global target_location_is_safe
    global target_locatoin_is_obstacle
    print("Entering check_target_location: ", end = '')
    print(target_location)
    if(world_map[target_location[X]][target_location[Y]] == obstacle_present):
        target_location_is_safe = no
        target_location_obstacle = yes
    else:
        target_location_is_safe = yes
        target_location_obstacle = no

def list_of_movement():
    global move_direction

    print("Entering list_of_movement")
    move_direction[X] = target_location[X] - current_location[X]
    move_direction[Y] = target_location[Y] - current_location[Y]
    print("move_direction:", end = '')
    print(move_direction)
    #This is not considering the possibilities of obstacles

def make_movement():
    print("Entering make_movement")
    while(move_direction[X] != 0 or move_direction[Y] != 0):
        if move_direction[X] > 0: #Positive X differences
            move_east()
        elif move_direction[X] < 0:
            move_west()
        elif move_direction[Y] > 0:
            move_north()
        elif move_direction[Y] < 0:
            move_south()
        list_of_movement()

def display_capacitor_reading():
    print("Entering display_capacitor_reading")
    lightmatrix_update_simple(current_location[X], current_location[Y], \
    max_capacitor_index)

    return
    

def remove_target_block():
    global default_path
    print("Entering remove_target_block")
    default_path.pop(0)

def move_north():
    print("North")
    move_y(pos_direction)
    current_location[Y] += 1
    return
def move_south():
    print("South")
    move_y(neg_direction)
    current_location[Y] += -1
    return
def move_east():
    print("East")
    move_x(pos_direction)
    current_location[X] += 1
    return
def move_west():
    print("West")
    move_x(neg_direction)
    current_location[X] += -1
    return

def get_sensor():
    print("Entering get_sensor")
    global block_direction
    global max_capacitor_index

    block_direction = us_sensor()
    print("Ultrasonic Readings: ", end = '')
    print(block_direction)
    current_capacitor_block_array = capacitor_block_multiple(2)

    print("List Received from Function:")
    print(current_capacitor_block_array)
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
    max_capacitor_index = current_capacitor_block_array.index(max(current_capacitor_block_array))

    left_y = (current_location[X] != 0 and current_location[Y] > 0 and \
    current_location[Y] < 6)
    right_y = (current_location[X] != 6 and current_location[Y] > 0 and \
    current_location[Y] < 6)
    bottom_x = (current_location[Y] != 0 and current_location[X] > 0 and \
    current_location[X] < 6)
    top_x = (current_location[Y] != 6 and current_location[X] > 0 and \
    current_location[X] < 6)

    if(left_y or right_y or bottom_x or top_x):
        if(max_capacitor_index == wire and max(block_direction) >= 10):
            print("Recalibrating from reference block: wire")
            capacitor_constant_rewrite(wire)
        if(max_capacitor_index == insulation and max(block_direction) >= 10):
            print("Recalibrating from reference block: insulated")
            capacitor_constant_rewrite(insulation)

    print("max_index: {A}".format(A = max_capacitor_index))

    return

