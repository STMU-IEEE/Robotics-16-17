#!/usr/bin/env python3
from function import *
from senseHat import *
#from function import restart_comm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

FRONT_C = 1
LEFT_C = 2
RIGHT_C = 3
BACK_C = 4

#This are for testing the senseHat.py
x_pos = 0
y_pos = 0

#Switch Case that selects the commands
def command(x):
	global x_pos
	global y_pos

	data_in = x.split()

	#Motor Commands
	if data_in[0] == 'w':
		move_forward(data_in)
	if data_in[0] == 'a':
		move_left(data_in)
	if data_in[0] == 's':
		move_reverse(data_in)
	if data_in[0] == 'd':
		move_right(data_in)
	if data_in[0] == 'x':
		stop()
	if data_in[0] == 'q':
		rotate_counter(data_in)
	if data_in[0] == 'e':
		rotate_clockwise(data_in)
	#Calibration and Distance Commands
	if data_in[0] == 'm':
		encoder_calibration(int(data_in[1]), int(data_in[2]))#Byte one(0 for Y and 1 for X), Byte Two(quantity of test)
	if data_in[0] == 'M':
		encoder_update()
	if data_in[0] == 'K':
		encoder_reset()
	if data_in[0] == 'B':
		encoder_update()
		encoder_current_value()
	if data_in[0] == 'H':
		encoder_constant_value()
	#regarding side, 0 is for positive direction, while 1 is for negative directions
	if data_in[0] == 'X':
		move_x(data_in[1])#side, speed
		#Just for testing purposes
		if(data_in[1] == '0'):
			x_pos += 1
		if(data_in[1] == '1'):
			x_pos += -1
	if data_in[0] == 'Y':
		move_y(data_in[1])
		#Just for testing purposes
		if(data_in[1] == '0'):
			y_pos += 1
		if(data_in[1] == '1'):
			y_pos += -1
	#Sensor Commands
	if data_in[0] == 'u':
		print(us_sensor())
	if data_in[0] == 'o':#reading the values of the capacitor sensor
		capacitor_sensor()
	if data_in[0] == '|':
		capacitor_report()
	if data_in[0] == 'h':
		capacitor_hard_reset()
	if data_in[0] == 'l':
		capacitor_calibration()
	if data_in[0] == 'v':
		print(capacitor_block_identity())#0 wire, 1 no wire no insulation, 2 insulation
	if data_in[0] == 'L':
		capacitor_calibrate_move(int(data_in[1]), int(data_in[2]), int(data_in[3]))#1: block identity,2: quantity of data samples 3: use previous values?
	if data_in[0] == 'V':
		cap_block_score = capacitor_block_multiple(int(data_in[1]))# # of test
		print("X:\t{A}\tY:{B}".format(A = x_pos, B = y_pos))
		lightmatrix_update(x_pos,y_pos,cap_block_score)
	#Servo Command
	if data_in[0] == 't':
		servo_top(data_in[1])
	if data_in[0] == 'b':
		servo_bottom(data_in[1])
	if data_in[0] == 'n':
		servo_info()
	if data_in[0] == 'c':
		servo_change(data_in)
	if data_in[0] == 'p':
		servo_bottom(data_in[1])
		sleep(5)
		servo_top(data_in[1])
	if data_in[0] == '}':
		pick_up_lid( int(data_in[1]),int(data_in[2]), int(data_in[3]) )#which_arduino, axes, direction
	#Communicatin Command
	if data_in[0] == 'R':
		restart_comm()
	if data_in[0] == 'C':
		clear_comm()
	"""
        Raspberry Pi Gyro Commands
	#Gyro Commands
	if data_in[0] == 'W':
		move_gyro(FRONT_C, data_in[1], data_in[2])
	if data_in[0] == 'A':
		move_gyro(LEFT_C, data_in[1], data_in[2])
	if data_in[0] == 'D':
		move_gyro(RIGHT_C, data_in[1], data_in[2])
	if data_in[0] == 'S':
		move_gyro(LEFT_C, data_in[1], data_in[2])
	if data_in[0] == 'Q':
		rotate_counter_gyro()
	if data_in[0] == 'E':
		rotate_clockwise_gyro()
	if data_in[0] == 'P':
		redefine_pre()
	if data_in[0] == 'F':
		redefine_fre(data_in[1])
	if data_in[0] == 'I':
		redefine_sensa(data_in[1])
	if data_in[0] == 'T':#testing
		redefine_pre()
		gyro_main()
	#Magnetometer Commands
	if data_in[0] == 'N':
		north()
	"""
	#Arduino Gyro Commands

	if data_in[0] == '=':
		gyro_cali()
	if data_in[0] == '?':
		gyro_update_angle()
		gyro_report_angle()
	if data_in[0] == '[':
		gyro_PID_test()
	if data_in[0] == '>':
		gyro_angle_test()



	return

#Here is the loop that receives data_in from the user

print("Welcome to The Raspberry Pi Controller HQ")
print("FRONT: 1, LEFT: 2, RIGHT: 3, BACK: 4")
print("Variable Speed: [direction (wasd) and x to stop] [Left A] [Left B] [Right A] [Right B]")
print("Move by axes and block: [direction (X or Y)] [positive(0) or negative(1)] 1 ")
print("Servo: FRONT = 1 BACK = 4 --> [up(t) or down(b) or pick_up(p)] [servo#]")
print("Gyro: [direction (caps motor's keys)] [max_speed] [gryo_sensativity]")
print("Communication Commands: [command (R or C)]")
print("Ultrasonic Sensor: 'u' ")
#print('Flushing inputs...')
#clear_comm()
print('Restarting communication...')
restart_comm()
print('Stopping motors...')
stop()
print('Checking if gyros initialized...')
read_gyro_status()
print('Assign IDs...')
assign_side()
print('Calibrating gyros...')
gyro_cali()
print('Clearing the previous matrix...')
lightmatrix_no_color()
print('Enabling Yellow Ready Light')
lightmatrix_yellow()
#servo_top()
init_loop = True
while(True):
	x = input("Enter Command: ")
	if(init_loop):
		#on the first time through the loop, blank the LED screen
		init_loop = False
		lightmatrix_no_color();
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)
# TODO: Make Sure that the arduinos are no longer sending any values. at all.
print('Clearing LED Matrix and Quitting...')
lightmatrix_no_color()
GPIO.cleanup()
