from Pathfinding import *
from function import *
from senseHat import *
from display import *
run_pres = 0

#Function that occurs when stop and/or start button are pressed

def start_button_pressed(channel):
	#This is where the program to solve the "maze" would go
	#for now it just makes the robot move foward

	#TODO: Restart Comm is causing this function to fail
	#restart_comm()
	global run_pres
	global cali_pres
	global test_light
	print("GO Button Pressed")
	sleep(0.2)

	if(cali_pres == 1):
		print("Calibration detected")
		print("Cali_pres returned to 0")
		cali_pres = 0

	run_pres = 1
	return

def stop_button_pressed(channel):
	print("STOP Button Pressed")
	exit()

#Assigned the interrupt their functions
if GPIO.getmode() is None:
	GPIO.setmode(GPIO.BOARD)
#Setting up the Interrupt
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)
sleep(1) # DO NOT DELETE!
 # This delay must be present for proper functioning.
 # Without the delay, the pull-up resistor connecting
 # will raise the level, causing an interrupt
 # as soon as the interrupt is enabled.
GPIO.add_event_detect(37, GPIO.RISING, callback = start_button_pressed, bouncetime = 300) # GPIO-26
# GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.add_event_detect(36, GPIO.FALLING, callback = stop_button_pressed, bouncetime = 300) # GPIO-26

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
#Using the variables from pathfinding
# global default_path
# global world_map
print('Waiting for button to be pressed...')
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
