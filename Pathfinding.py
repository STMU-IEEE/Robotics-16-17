#
#    [0]A  [1]B  [2]C  [3]D  [4]E  [5]F  [6]G
#   +-----+-----+-----+-----+-----+-----+-----+
#[0]|     |     |     |     |     |     |     |
# 1 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[1]|     |     |     |     |     |     |     |
# 2 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[2]|     |     |     |     |     |     |     |
# 3 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[3]|     |     |     |     |     |     |     |
# 4 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[4]|     |     |     |     |     |     |     |
# 5 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[5]|     |     |     |     |     |     |     |
# 6 |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |
#   +-----------------------------------------+
#[6]|START|     |     |     |     |     |     |
# 7 |  X  |     |     |     |     |     |     |
#   |HE RE|     |     |     |     |     |     |
#   +-----+-----+-----+-----+-----+-----+-----+

import numpy as np
# from heapq import *

blocked_vals = {-1}  # this is a list of the possible blocked values for pathfinding purposes
my_location = (0,0) # first val for vert, second for horiz (row, col)

world_map = np.full((7,7), 8, dtype=np.int)
# unexplored blocks will have a travel cost value of 8.
# this travel cost will be reduced to 1 when the robot explores that region.
flow_map = []



def follow(path, globalPath):

    while path:
        world_map[my_location[0]][my_location[1]]=(1)
        # run sensors and \
        get_sensors()
        # update the map here


        if next_pos[0] > my_location[0]: # if we are south of the next point
            move_north()
        elif next_pos[0] < my_location[0]: # if we are north of the next point
            move_south()
        elif next_pos[1] > my_location[1]: #if we are east of the next point
            move_west()
        else:
            move_east()

def you_are_here(): #for debug purposes
    view_map = world_map
    view_map[my_location[0]][my_location[1]] = 'X'
    print(view_map)

def dist(a, b):
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) **.5

def get_sensors():
    neighbor_dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    for i,j in neighbor_dirs:
        if 0 <= neighbor[0] < world_map.shape[0]:
            if 0 <= neighbor[1] < world_map.shape[1]:
                world_map[i][j] = obstacles[i][j]
            else:
                # vertical bounds
                continue
        else:
            # horizontal bounds
            continue
    return

def flowField(world, target):
    output_field = np.zeros((7,7,2), dtype=np.int)
    neighbor_dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    closed_set = set();
    parents = {}
    g_score = {start:0}
    open_set = set(); # list of nodes to be explored

    open_set.add(target);


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



    return True

# def aStar(world, start, goal):
#     neighbor_dirs = [(0,1),(0,-1),(1,0),(-1,0)] #,(1,1),(1,-1),(-1,1),(-1,-1)]
#                                                 #INCLUDE THESE FOR DIAGONALS
#
#     closed_set  = set()     # this is the set of checked nodes
#     parents     = {}        # list of inheritances to reconstruct path at the end
#     g_score     = {start:0} #
#     f_score     = {start:dist(start, goal)}
#     open_set    = []        # list of nodes to be explored.
#                             # <kept in a n ordered heap for better search times>
#
#     heappush(open_set, (fscore[start], start))
#         # start the search at the start location
#     while oheap:
#         current_loc = heappop(open_set)[1]
#         if current_loc == goal:
#             path = []
#             while current_loc in parents:
#                 path.append(current_loc)
#                 current_loc = came_from[current]
#             path.reverse() #the path is calculated from goal to start, reverse for path from start to goal.
#             return path
#
#             closed_set.add(current)
#             for i, j in neighbor_dirs:
#                 neighbor = current_loc[0] + i, current_loc[1] + j
#                 tentative_g = g_score[current_loc] + dist(current_loc)
#                 if 0 <= neighbor[0] < world.shape[0]:
#                     if 0 <= neighbor[1] < world.shape[1]:
#                         if array[neighbor[0]][neighbor[1]] in blocked_vals:
#                             continue
#                     else:
#                         # vertical bounds
#                         continue
#                 else:
#                     # horizontal bounds
#                     continue
#
#                 if neighbor in closed_set and tentative_g >= g_score.get(neighbor, 0):
#                     continue
#
#                 if tentative_g < g_score.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
#                     parents[neighbor] = current
#                     g_score[neighbor] = tentative_g
#                     f_score[neighbor] = tentative_g + dist(neighbor, goal)
#                     heappush(oheap, (f_score[neighbor], neighbor))
#     return false
