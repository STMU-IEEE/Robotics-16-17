from Pathfinding import *
from function import *
from senseHat import *
from display import *
global run_pres

##INITALIZATION

debug_light_num = 0
print('Restarting communication...')
debug_light_num = debug_light_num+1
lightmatrix_debug(debug_light_num)
restart_comm()

print('Stopping motors...')
stop()
debug_light_num = debug_light_num+1
lightmatrix_debug(debug_light_num)

print('Checking if gyros initialized...')
read_gyro_status()
debug_light_num = debug_light_num+1
lightmatrix_debug(debug_light_num)

print('Assign IDs...')
assign_side()
debug_light_num = debug_light_num+1
lightmatrix_debug(debug_light_num)

print('Calibrating gyros...')
gyro_cali()
debug_light_num = debug_light_num+1
lightmatrix_debug(debug_light_num)

print('Calibrating capacitor sensor... (based of insulated block) ')
capacitor_calibrate_move(2,5,0)
capacitor_constant_rewrite(2)

print('Clearing the previous matrix...')
lightmatrix_no_color()
print('Enabling Yellow Ready Light')
lightmatrix_yellow()

print('Setting up seven segment display...')
seven_seg_setup()
print('Turning off seven segment display...')
seven_seg_turn_off()

global run_pres
run_pres = 0
#Using the variables from pathfinding
# global default_path
# global world_map

while(run_pres == 0):#Waiting for the "GO"
	sleep(0.01)
#Initialize the Run
lightmatrix_no_color()
lightmatrix_A7_yellow()
follow()
print("Path Completed!")
run_pres = 0

##
##Waiting for the GO button to be pressed
