import serial   #This requires Pyserial 3 or later
import sys
import RPi.GPIO as GPIO
import math
from sense_hat import SenseHat
from time import sleep, time
from colorama import Fore, Back, Style
from statistics import mean, median, median_low, median_high
from senseHat import *
from img_proc import *
from display import *
"""
install funsim's fork of ivPID from https://github.com/funsim/ivPID
`sudo python3 setup.py install`
"""
from ivPID.pid import PID


#Setting up communication between arduino and raspberry pi


LEFT_ARDUINO_PORT='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'
RIGHT_ARDUINO_PORT='/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'
BAUD = 57600
left = serial.Serial(LEFT_ARDUINO_PORT, BAUD)
right = serial.Serial(RIGHT_ARDUINO_PORT, BAUD)

left.reset_input_buffer()
right.reset_input_buffer()
left.reset_output_buffer()
right.reset_output_buffer()

# manually reset Arduino by toggling DTR
left.dtr = False
right.dtr = False
sleep(0.01)
left.dtr = True
right.dtr = True


#left.open()
#right.open()
# Arduinos require about 3 seconds before finishing setup()
print('Wait for Arduinos to finish resetting...')
sleep(2)

#left.timeout = 0.1
#right.timeout = 0.1

# gyro PID object (rotation)
gyro_pid = PID(P=1.0, I=0.0, D=0.0) # only P term (-1.0 power per degree error); not really PID!
gyro_pid.setSampleTime(1.0/30.0) #30Hz. Increase if "wobbling"; decrease if losing data
gyro_pid_old_output = 0.0 # initial value

# ultrasonic PID object (distance)
us_pid = PID(P=1.0, I=0.0, D=0.0) # only P term
us_pid.setSampleTime(1.0/30.0) # not relevant unless I or D terms are used
us_pid_old_output = 0.0 # initial value

#Direction and Arduino Variables
FRONT = 1
LEFT = 2
RIGHT = 3
BACK = 4

Y = 0
X = 1

LEFT_ARDUINO_ID = 0
RIGHT_ARDUINO_ID = 1

POS_DIRECTION = 0
NEG_DIRECTION = 1

yes = 1
no = 0

cali_pres = 0
run_pres = 0

#Encoder Variables
encoder_value = [0,0,0,0] #left A, left B, right A, right B
encoder_constant_x = [2850,2850,2850,2850] #value of encoders to reach one block
encoder_constant_y = [2900,2900,2900,2900]
encoder_constant = [encoder_constant_y, encoder_constant_x]

#Movement Variables
move_x_speed_p = [215,190,200,205]
move_x_speed_n = [210,185,210,185]
move_y_speed_p = [165,165,200,200]
move_y_speed_n = [180,180,200,200]

current_speed = [0,0,0,0]

move_x_speed = [move_x_speed_p, move_x_speed_n]
move_y_speed = [move_y_speed_p, move_y_speed_n]

move_speed = [move_y_speed, move_x_speed]

#Capacitor Variables
capacitor_data_wire = [0,0,0,0]#max,median,min,average
capacitor_data_iso = [0,0,0,0]
capacitor_data_notiso = [0,0,0,0]

capacitor_data_constant = [capacitor_data_wire, capacitor_data_notiso, capacitor_data_iso]
capacitor_data_based_wire = [[0,0,0,0],[-250,-250,-280,-260],[-340,-340,-340,-340]]
capacitor_data_based_iso = [[340,340,340,340],[35,40,33,11],[0,0,0,0]]
capacitor_data_based_group = [capacitor_data_based_wire,[], capacitor_data_based_iso]


capacitor_data_current = [0,0,0,0]#place holder for the newest data from the capacitor sensor

capacitor_block_score = [0,0,0]#This will hold the scores of mutiple
#data samples from the capacitor_block_identity

#Gyro Variables
gyro_angle = [0,0] #Left, Right
gyro_cali_b = b'='
gyro_update_angle_b = b'?'
gyro_is_calibrated = no

#Communication Constants
TERM_CHAR = ' '
END_CHAR = '\n'
CONFIRM_CHAR = '@'
EMERGENCY_CHAR = '%'

#Ultrasonic Variables
ultra_ave = [0,0,0,0]


#functions that control the arduino

#-----------------GENERAL PURPOSE-------------------
def assign_side():
	left.write(b']')
	right.write(b']')
	left.write(str(LEFT_ARDUINO_ID).encode())
	right.write(str(RIGHT_ARDUINO_ID).encode())
	return

def arduino_data_ready(side_arduino):
	if(side_arduino == LEFT_ARDUINO_ID):
		while(left.in_waiting == 0):
			sleep(0.001)
	if(side_arduino == RIGHT_ARDUINO_ID):
		while(right.in_waiting == 0):
			sleep(0.001)
	return True

def read_arduino(side_arduino,with_confirmation):
	#side if 1 means left and 2 means right
	#TERM_CHAR separates values
	#END_CHAR ends of transmition


	if(side_arduino == LEFT_ARDUINO_ID and arduino_data_ready(LEFT_ARDUINO_ID)):
			#TODO: What is the 25 argument for? readline() doesn't expect any arguments.
		bline = left.readline()
		if(with_confirmation):
			left.write(CONFIRM_CHAR.encode())
	if(side_arduino == RIGHT_ARDUINO_ID and arduino_data_ready(RIGHT_ARDUINO_ID)):
		bline = right.readline()
		if(with_confirmation):
			right.write(CONFIRM_CHAR.encode())

	print(bline)

	#TODO: this should not happen/be necessary
	'''
	if('^' in bline.decode()):#Unknown Arduino
		print("Found ^")
		restart_comm()
		read_gyro_status()
		assign_side()
		return []
	'''
	if(EMERGENCY_CHAR in bline.decode()):#Emergency Char '%'
		sleep(0.1)
		print("FOUND EMERGENCY CHAR")
		return None
	#split() will remove '\r'
	'''
	if(bline == b'\r'):
		print("Found backlash r")
		return []
	'''
	trans_array = [float(s) for s in bline.decode().split()]

	return trans_array




#-----------------COMMUNICATION-------------------
def end():
	"Stops the motors and disconnects the serial comm channels."##LINE 20
	stop()
	right.close()
	left.close()
	return
def clear_comm():
	left.reset_input_buffer()
	right.reset_input_buffer()
	return

def clear_comm_absolute():
	while(len(left.read()) == 0):
		left.flushInput()
	while(len(right.read()) == 0):
		right.flushInput()
	return

def restart_comm():
	left.write(b"R")
	right.write(b"R")
	response = read_arduino(LEFT_ARDUINO_ID,no)
	if(response[0] != 1):
		print("Incorrect response '{A}' from left arduino". \
		format(A=repr(response)))
	response = read_arduino(RIGHT_ARDUINO_ID,no)
	if(response[0] != 1):
		print("Incorrect response '{A}' from right arduino". \
		format(A=repr(response)))
	return



#-----------------MOVEMENT------------------------
def stop():
	right.write(b"x")
	left.write(b"x")
	return

def move_right(data_in):
	left.write(b"i")
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())#separator char
	left.write(data_in[2].encode() )
	left.write(END_CHAR.encode())

	right.write(b"o")
	right.write(data_in[3].encode() )
	right.write(END_CHAR.encode())#separator char
	right.write(data_in[4].encode() )
	right.write(END_CHAR.encode())
	return

def move_left(data_in):
	left.write(b"o")
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())#Separator Char
	left.write(data_in[2].encode() )
	left.write(END_CHAR.encode())

	right.write(b"i")
	right.write(data_in[3].encode() )
	right.write(END_CHAR.encode())#Separator Char
	right.write(data_in[4].encode() )
	right.write(END_CHAR.encode())
	return
##LINE 40

def move_forward(data_in):
	print("Forward Function")
	print(data_in)
	left.write(b"w")
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())#Separator Char
	left.write(data_in[2].encode() )
	left.write(END_CHAR.encode())
	#sleep(1)
	right.write(b"w")
	right.write(data_in[3].encode() )
	right.write(END_CHAR.encode())#Separator Char
	right.write(data_in[4].encode() )
	right.write(END_CHAR.encode())
	return

def move_reverse(data_in):

	left.write(b"r")
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())#Separator Char
	left.write(data_in[2].encode() )
	left.write(END_CHAR.encode())

	right.write(b"r")
	right.write(data_in[3].encode() )
	right.write(END_CHAR.encode())#Separator Char
	right.write(data_in[4].encode() )
	right.write(END_CHAR.encode())
	return

def rotate_counter(data_in):
	#counter clockwise --> left reverse, right forward
	left.write(b"r")
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())

	right.write(b"w")
	right.write(data_in[1].encode() )
	right.write(END_CHAR.encode())
	right.write(data_in[1].encode() )
	right.write(END_CHAR.encode())
	return

def rotate_clockwise(data_in):
	#counter clockwise --> left forward, right reverse
	left.write(b"w")
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())

	right.write(b"r")
	right.write(data_in[1].encode() )
	right.write(END_CHAR.encode())
	right.write(data_in[1].encode() )
	right.write(END_CHAR.encode())

	return

#-----------------ENCODERS------------------------
def encoder_calibration(axes,test_quantity):
	test_sample = [0,0,0,0]

	print("Calibration Iniciated")
	if axes == Y:
		print("Y axis selected")
	if axes == X:
		print("X axis selected")
	print("Quantity of test: {A}".format(A = test_quantity))

	global cali_pres

	for i in range(test_quantity):

		encoder_reset()
		print("Beginning test {A}".format(A = i+1))

		cali_pres = 1

		data_in = ['@','@', '@', '@', '@']

		if(axes == Y):#Y Calibration
			for i in range(4):
				print("Motor speed changed to Y+ default")
				data_in[i + 1] = str(move_y_speed_p[i])
			move_forward(data_in)
		if(axes == X):#X Calibration
			for i in range(4):
				print("Motor speed changed to X+ default")
				data_in[i + 1] = str(move_x_speed_p[i])
			move_right(data_in)

		while(cali_pres == 1):
			sleep(0.001)
		print("Stopwatch stop!")
		stop()
		encoder_update()
		for i in range(4):
			test_sample[i] = test_sample[i] + encoder_value[i]
		stop()

	for i in range(4):
			test_sample[i] = test_sample[i] / test_quantity

	for i in range(4):#Transferring average to constant variable
		if axes == Y:#Y
			encoder_constant_y[i] = test_sample[i]
			print("{A}: {B}".format(A = i, B = encoder_constant_y[i]))
		if axes == X:#X
			encoder_constant_x[i] = test_sample[i]
			print("{A}: {B}".format(A = i, B = encoder_constant_x[i]))
	stop()
	return


def encoder_update():#1 for Y, 2 for X
#TODO: ???
	#clear_comm()

	left.write(b"m")
	right.write(b"m")

	global encoder_value
	encoder_holder = read_arduino(LEFT_ARDUINO_ID, no)

	encoder_value[0] = encoder_holder[0]
	encoder_value[1] = encoder_holder[1]

	encoder_holder = read_arduino(RIGHT_ARDUINO_ID, no)
	encoder_value[2] = encoder_holder[0]
	encoder_value[3] = encoder_holder[1]

	print(encoder_value)

	return

def encoder_reset():

	left.write(b"k")
	right.write(b"k")

	encoder_update()

	return

def encoder_current_value():
	encoder_update()
	print("Current values of Encoders")
	print("Encoder Values")
	print("Left A: {A1} B: {B1} Right A: {A2} B: {B2}" \
		.format(A1 = encoder_value[0], B1 = encoder_value[1], \
			A2 = encoder_value[2], B2 = encoder_value[3] ) )

	return


def encoder_constant_value():
	print("Constant values of Encoders")
	print("Encoder Values for Y Axis")
	print("Left A: {A1} B: {B1} Right A: {A2} B: {B2}" \
		.format(A1 = encoder_constant_y[0], B1 = encoder_constant_y[1], \
			A2 = encoder_constant_y[2], B2 = encoder_constant_y[3] ) )
	print("Encoder Values for X Axis")
	print("Left A: {A1} B: {B1} Right A: {A2} B: {B2}" \
		.format(A1 = encoder_constant_x[0], B1 = encoder_constant_x[1], \
			A2 = encoder_constant_x[2], B2 = encoder_constant_x[3] ) )
	return

def encoder_completion(axes):
	completion = 0
	for i in range(4):
		if(int(encoder_value[i]) >= mean(encoder_constant[axes])):
			completion = completion + 1

	if(completion >= 3):
		return 1

	return 0

def move_y(direction):
	direction = int(direction)
	print("Axes: Y Side:{A}".format(A = direction))

	encoder_reset()
	data_in = ['0','0','0','0','0']

	for i in range(4):
		data_in[i+1] = str(move_y_speed[direction][i])

	if(direction == POS_DIRECTION):
		move_forward(data_in)
	if(direction == NEG_DIRECTION):
		move_reverse(data_in)

	#encoder_constant_value()
	#if the function returns 0, that means that non of the encoders have reach the desired value
	while(encoder_completion(Y) == 0):
		encoder_update()
		print(update_PID())
		new_motor_speed = obtain_new_motor_speeds(Y,direction, gyro_pid.output)
		update_motor_speed(Y,direction, new_motor_speed )
	stop()

	return

def move_x(direction):
	direction = int(direction)
	print("Axes: X Side:{A}".format(A = direction))

	encoder_reset()
	data_in = ['0','0','0','0','0']

	for i in range(4):
		data_in[i+1] = str(move_x_speed[direction][i])

	if(direction == POS_DIRECTION):
		move_right(data_in)
	if(direction == NEG_DIRECTION):
		move_left(data_in)


	#encoder_constant_value()
	#if the function returns 0, that means that non of the encoders have reach the desired value
	while(encoder_completion(X) == 0):
		encoder_update()
		update_PID()
		new_motor_speed = obtain_new_motor_speeds(X,direction, gyro_pid.output)
		update_motor_speed(X,direction,new_motor_speed)
	stop()

	return

#-----------------SENSORS-------------------


#-----------------ULTRASONIC----------------
def us_sensor():
	actual_sensor_collect_fre = 0
	sensor_collect_fre = 5
	clear_comm()

	sensor_total = [0,0,0,0]#left_back, left_left, right_front, right_right
	sensor_collect = [0,0,0,0]
	trash_value = 0
	sensor_holder_right = [0,0]
	sensor_holder_left = [0,0]

	for i in range(sensor_collect_fre):

		left.write(b"u")
		right.write(b"u")

		sensor_holder_left = read_arduino(LEFT_ARDUINO_ID,no)
		sensor_holder_right = read_arduino(RIGHT_ARDUINO_ID,no)

		if(len(sensor_holder_left) < 2 and len(sensor_holder_right) < 2):
			print("*")
			continue

		actual_sensor_collect_fre += 1
		sensor_collect = sensor_holder_left + sensor_holder_right

		#The ultrasonic sensor will return 0 if max(200) if reached
		#Still debating whether to make it equal to zero or max
		#Sometime max can be misread when the sensor might be too close to a wall
		for i in range(4):
			if(sensor_collect[i] == 0):
				sensor_collect[i] = 100


		sensor_total[0] += sensor_collect[0]
		sensor_total[1] += sensor_collect[1]

		sensor_total[2] += sensor_collect[2]
		sensor_total[3] += sensor_collect[3]


	left_back_ave = sensor_total[0] / actual_sensor_collect_fre
	left_left_ave = sensor_total[1] / actual_sensor_collect_fre

	right_front_ave = sensor_total[2] / actual_sensor_collect_fre
	right_right_ave = sensor_total[3] / actual_sensor_collect_fre


	print("LEFT: B:{B}	L:{L}	RIGHT: F:{F}	R:{R}" \
		.format(B = left_back_ave,L = left_left_ave, \
			F = right_front_ave, R = right_right_ave ) )

	# North 1000
	# South 0100
	# East	0010
	# West	0001

	ultra_ave = [right_front_ave, left_back_ave, right_right_ave, left_left_ave]

	block_direction = [0,0,0,0]

	block_message = 0
	for i in range(4):
		if(ultra_ave[i] <= 12):
			block_direction[i] = 1

	#print(block_direction)
	for i in range(4):
		if(block_direction[i] == 1):
			block_message = block_message + pow(10,3-i)

	#print("Block Message: ", end = '')
	#print(block_message)

	print("Block Direction : ", end = '')

	return block_direction
"""
we can use the data of the ultrasonic sensor to get more reliable data
def wall_calibration()

"""
#-----------------CAPACITOR-------------------

def capacitor_sensor():
	#The right arduino is the only arduino with a capacitive sensor
	#capacitor_hard_reset()
	sensor_data = [-2,-2,-2,-2] #Highest, median, lowest, average
	#clear_comm()
	flag = 0

	print("Collecting data from Capacitive Sensor")

	for i in range(20):#This is the amount of attempts the Raspberry has to receive the information
		flag = 0
		#clear_comm()
		right.write(b"C")
		#sleep(0.5)
		#capacitor_hard_reset()
		sensor_data = read_arduino(RIGHT_ARDUINO_ID, yes)
		print(sensor_data)

		if(sensor_data is None or len(sensor_data) == 0):
			continue

		for i in range(len(sensor_data)):#If any of the values is a trash value
			if(sensor_data[i] < 10000 and sensor_data[i] > -2):#To small
				#print("Trash Value Detected: Cut off")
				print("C, ", end = '')
				flag = 1
				continue
			if(sensor_data[i] > 100000):#Too big
				#print("Trash Value Detected: Run on")
				print("R, ", end = '')
				flag = 1
				continue
			if(sensor_data[i] == -2):
				#print("Communication Failure")
				print("F, ", end = '')
				flag = 1
				continue
			#These cases should not happen. This means your sort is bad!
			if(sensor_data[2] > sensor_data[1]):
				print("B, ", end = '')
				flag = 1
				continue
			if(sensor_data[0] < sensor_data[1]):
				print("b, ", end = '')
				flag = 1
				continue

		if(flag == 1):
			continue
		break

	for i in range(4):
		if(sensor_data is not None):
			capacitor_data_current[i] = sensor_data[i]

	clear_comm()
	return

def capacitor_report():
	print("Value of Capacitor Data Current now:\t", end = '')
	print(capacitor_data_current)
	return

def capacitor_constant_diff_rewrite(reference_block):
	#To check the difference between the constanst respect to the insulated block
	#The insulated block has been chosen to be the reference block
	#Since it is going to be the block at A7

	print("Value of Capacitor Constants Data: ", end = '')
	print(capacitor_data_constant)

	for x in range(len(capacitor_data_constant)):
		for y in range(len(capacitor_data_constant[x])):
			capacitor_data_based_group[reference_block][x][y] = \
			capacitor_data_constant[x][y] - capacitor_data_constant[reference_block][y]

	print("Differences of the Capacitor Constants comparing to the Insulated Block:")
	print(capacitor_data_based_group[reference_block])
	return

def capacitor_constant_rewrite(reference_block):

	#This changes the values of the constant in respect to the
	#reference block, which could be either wire or insulated block

	for x in range(len(capacitor_data_constant)):
		for y in range(len(capacitor_data_constant[x])):
			capacitor_data_constant[x][y] = \
			capacitor_data_constant[reference_block][y] + capacitor_data_based_group[reference_block][x][y]

	return


def capacitor_hard_reset():
	right.write(b"H")
	print("Capacitor sensor reset")
	#This lets the capacitor reset
	return

def capacitor_trash_value():
	flag = False
	for i in range(4):
		if(capacitor_data_current[i] > 100000 \
		or capacitor_data_current[i] < 10000 \
		or capacitor_data_current[i] == -2):
			flag = True
			print("Capacitor_trash_value found trash value")
			break

	return flag

def capacitor_fix_value():
	while(capacitor_trash_value == True):
		print("Recalculating values")
		capacitor_sensor()
	return

def capacitor_calibration():

	print("Iniciating Capacitor Sensor Calibration")
	print("Order of Calibration:")
	print("\tNot Isolated with Wire")
	print("\tNot Isolated without Wire")
	print("\tIsolated")

	global cali_pres
	for i in range(3):
		cali_pres = 1

		print("Step {A}".format(A = i + 1))

		if(i == 0):#Wire
			print("Place on non-Isolated Block with Wire")
		if(i == 1):#Not isolated with no wire
			print("Place on non-Isolated Block without Wire")
		if(i == 2):#Isolated
			print("Place on Isolated Block")

		while(cali_pres == 1):
			sleep(0.02)

		capacitor_sensor()

		for j in range(4):
			capacitor_data_constant[i][j] = capacitor_data_current[j]


def capacitor_calibrate_move(block_calibrate, data_sample, use_pre):
	print("Calibration Iniciated: Movement Procedure")
	print("Identity Calibrated: ", end = '')
	divider = data_sample
	data_holder = [0,0,0,0]


	if(use_pre == 1):
		divider = divider + 1
		for u in range(4):
			data_holder[u] = capacitor_data_constant[block_calibrate][u]

	print("Using this as the pre_value: ", end = '')
	print(data_holder)


	for i in range(data_sample):
		capacitor_sensor()
		capacitor_fix_value()
		for h in range(4):
			data_holder[h] = int(capacitor_data_current[h]) + data_holder[h]

	#print("Total: ", end = '')
	#print(data_holder)

	for k in range(4):
		data_holder[k] /= divider

	for j in range(4):
		capacitor_data_constant[block_calibrate][j] = round(data_holder[j])

	if(block_calibrate == 0):
		print("Not Isolated with Wire is now: ", end = '')
	if(block_calibrate == 1):
		print("Not Isolated without Wire is now: ", end = '')
	if(block_calibrate == 2):
		print("Isolated is now: ", end = '')
	print(capacitor_data_constant[block_calibrate])

"""
This code appears to worsen sensor accuracy
def capacitor_calibrate_update(block_calibrate):

	print("Updating Block Data")
	print("Before update Calibrate")

	print(capacitor_data_constant[block_calibrate])

	for u in range(4):
		capacitor_data_constant[block_calibrate][u] = round((capacitor_data_current[u] + capacitor_data_constant[block_calibrate][u])/2)

	print("After update Calibrate")

	print(capacitor_data_constant[block_calibrate])
"""

def capacitor_block_identity():
	#first check if calibration has been done
	block_identity_message = 0
	diff_rating = [0,0,0]

	diff_wire = [0,0,0,0]
	diff_notiso = [0,0,0,0]
	diff_iso = [0,0,0,0]
	diff_wire_total = 0
	diff_notiso_total = 0
	diff_iso_total = 0

	if(capacitor_data_wire[0] == 0):
		print("WARNING")
		print("Recommended recalibration of the Capacitor Sensor")

	print("\nValues of the Constants for each block")

	print("Not Isolated with Wire")
	print("\t", end = '')
	print(capacitor_data_constant[0])

	print("Not Isolated without Wire")
	print("\t", end = '')
	print(capacitor_data_constant[1])

	print("Isolated")
	print("\t", end = '')
	print(capacitor_data_constant[2])

	capacitor_sensor()

	#Compare the current values of the sensor with the constants of each block
	print("")
	for i in range(4):
		diff_wire[i] = abs(capacitor_data_current[i] - capacitor_data_wire[i])
		diff_notiso[i] = abs(capacitor_data_current[i] - capacitor_data_notiso[i])
		diff_iso[i] = abs(capacitor_data_current[i] - capacitor_data_iso[i])
		#print("{A}\t{B}\t{C}".format(A = diff_wire[i],B = diff_notiso[i],C = diff_iso[i]))
	print("Differences")

	print("\tWire")
	print("\t\t", end = '')
	print(diff_wire)
	for j in range(4):
		diff_wire_total = diff_wire_total + diff_wire[j]
	print("\t\t\t",end = '')
	print(diff_wire_total)

	print("\tNot Isolated Without Wire")
	print("\t\t", end = '')
	print(diff_notiso)
	for j in range(4):
		diff_notiso_total = diff_notiso_total + diff_notiso[j]
	print("\t\t\t",end = '')
	print(diff_notiso_total)

	print("\tIsolated")
	print("\t\t", end = '')
	print(diff_iso)
	for j in range(4):
		diff_iso_total = diff_iso_total + diff_iso[j]
	print("\t\t\t",end = '')
	print(diff_iso_total)

	diff_max = [diff_wire[0], diff_notiso[0], diff_iso[0]]
	diff_median = [diff_wire[1], diff_notiso[1], diff_iso[2]]
	diff_min = [diff_wire[2], diff_notiso[2], diff_iso[2]]
	diff_ave = [diff_wire[3], diff_notiso[3], diff_iso[3]]
	diff_total = [diff_wire_total, diff_notiso_total, diff_iso_total]

	diff_all = [diff_max, diff_median, diff_min, diff_ave, diff_total]

	diff_index_min = [0,0,0,0,0]#max,median,min,ave,overall index
	diff_value_min = [0,0,0,0,0]#max,median,min,ave,overall values

	diff_holder = [0,0,0,0,0,0]#max,median,min,ave,overall

	diff_rating_max = 0
	diff_rating_max_index = 0

	diff_tolerance = 100
	diff_overpass_tolerance = 0

	"""
	print("Max")
	print(diff_max)
	print("Median")
	print(diff_median)
	print("Min")
	print(diff_min)
	print("Average")
	print(diff_ave)
	print("Total")
	print(diff_total)
	print("All")
	print(diff_all)
	"""

	for j in range(5):
		diff_index_min[j] = diff_all[j].index(min(diff_all[j]))
		diff_value_min[j] = diff_all[j][diff_index_min[j]]

	print("General Min Results")
	print(diff_index_min)
	print(diff_value_min)

	diff_rating[diff_index_min[0]] = diff_rating[diff_index_min[0]] + 1
	diff_rating[diff_index_min[1]] = diff_rating[diff_index_min[1]] + 2
	diff_rating[diff_index_min[2]] = diff_rating[diff_index_min[2]] + 1
	diff_rating[diff_index_min[3]] = diff_rating[diff_index_min[3]] + 2
	diff_rating[diff_index_min[4]] = diff_rating[diff_index_min[4]] + 1

	#Passing over the scores of a data samples
	for s in range(3):
		capacitor_block_score[s] += diff_rating[s]

	print("Difference Rating")
	print(diff_rating)

	diff_rating_max_index = diff_rating.index(max(diff_rating))
	diff_rating_max = diff_rating[diff_rating_max_index]

	block_identity_message = diff_rating_max_index

	#if all tied 2-2
	tied_check = 0

	return block_identity_message


def capacitor_block_multiple(data_sample):

	#resetting global variable
	for d in range(3):
		capacitor_block_score[d] = 0

	#Test the identities and let capacitor_block_score get some values
	for a in range(data_sample):
		sleep(0.75)
		print(capacitor_block_identity())

	#Find the max score
	index_highest_score = 0
	highest_score_value = 0
	for f in range(3):
		if(highest_score_value < capacitor_block_score[f]):
			highest_score_value = capacitor_block_score[f]
			index_highest_score = f

	print("Block Scores: ",end = '')
	print(capacitor_block_score)

	print("Block Identity: ", end = '')
	if(index_highest_score == 0):
		print("Not Isolated with Wire")
		block_identity_message = 0
	if(index_highest_score == 1):
		print("Not Isolated without Wire")
		block_identity_message = 1
	if(index_highest_score == 2):
		print("Isolated")
		block_identity_message = 2

	#return block_identity_message
	#For now I(Eduardo) would like to experiment how the robot would score
	#Each block before deciding which identiy the block is.
	return capacitor_block_score

#-----------------SERVOS-------------------

def servo_top(servo_location):
	servo_location = int(servo_location)

	if servo_location == RIGHT_ARDUINO_ID:
		right.write(b"t")
	if servo_location == LEFT_ARDUINO_ID:
		left.write(b"t")
	return

def servo_bottom(servo_location):
	servo_location = int(servo_location)

	if servo_location == RIGHT_ARDUINO_ID:
		right.write(b"b")
	if servo_location == LEFT_ARDUINO_ID:
		left.write(b"b")
	return

def servo_change(data_in):
	#data_in[1] = servoH_top
	#data_in[2] = servoH_bottom
	#Sending data_in to the left arduino
	left.write(data_in[0].encode() )
	left.write(data_in[1].encode() )
	left.write(END_CHAR.encode())#Separator Char
	left.write(data_in[2].encode() )
	left.write(END_CHAR.encode())
	#Sending data_in to the right arduino
	right.write(data_in[0].encode() )
	right.write(data_in[1].encode() )
	right.write(END_CHAR.encode())#Separator Char
	right.write(data_in[2].encode() )
	right.write(END_CHAR.encode())
	return

def servo_info():
	left.write(b"n")
	right.write(b"n")

	servo_holder = read_arduino(LEFT_ARDUINO_ID, no)

	left_servo_position = servo_holder[0]
	left_servo_height_top = servo_holder[1]
	left_servo_height_bottom = servo_holder[2]

	servo_holder = read_arduino(RIGHT_ARDUINO_ID , no)

	right_servo_position = servo_holder[0]
	right_servo_height_top = servo_holder[1]
	right_servo_height_bottom = servo_holder[2]

	print("Left Servo Information:")
	print("Position: {P} Height Top: {T} Height Bottom: {B}" \
		.format(P = left_servo_position, T = left_servo_height_top, \
			B = left_servo_height_bottom) )
	print("Right Servo Information:")
	print("Position: {P} Height Top: {T} Height Bottom: {B}" \
		.format(P = right_servo_position, T = right_servo_height_top, \
			B = right_servo_height_bottom) )

def encoder_completion_lid(axes):
	completion = 0

	lid_distance_ratio = 6
	encoder_constant_lid = [ [0], [0] ]
	encoder_constant_lid[axes] = \
		[x / lid_distance_ratio for x in encoder_constant[axes]]

	for i in range(4):
		if(int(encoder_value[i]) >= mean(encoder_constant_lid[axes])):
			completion = completion + 1

	if(completion >= 3):
		return 1

	return 0

def pick_up_lid(which_arduino,axes,direction):

	encoder_reset()
	data_in = ['0','0','0','0','0']

	for i in range(4):
		data_in[i+1] = str(round(move_speed[axes][direction][i]/2))

	if(axes == Y):
		if(direction == POS_DIRECTION):
			move_forward(data_in)
		if(direction == NEG_DIRECTION):
			move_reverse(data_in)
	if(axes == X):
		if(direction == POS_DIRECTION):
			move_right(data_in)
		if(direction == NEG_DIRECTION):
			move_left(data_in)
	#if the function returns 0, that means that non of the encoders
	#have reach the desired value
	while(encoder_completion_lid(axes) == 0):
		encoder_update()
	stop()
	sleep(0.2)
	servo_bottom(which_arduino)
	sleep(0.9)
	servo_top(which_arduino)

	#Now the robot must return to its previous place

	encoder_reset()
	sleep(0.5)

	if(axes == Y):
		if(direction == POS_DIRECTION):
			move_reverse(data_in)
		if(direction == NEG_DIRECTION):
			move_forward(data_in)
	if(axes == X):
		if(direction == POS_DIRECTION):
			move_left(data_in)
		if(direction == NEG_DIRECTION):
			move_right(data_in)

	#if the function returns 0, that means that non of the encoders
	#have reach the desired value
	while(encoder_completion_lid(axes) == 0):
		encoder_update()
		dice_read = dotCount()
		if(dice_read != 0):
			dice_face_m = dice_read
		print("M: {A}".format(A = dice_face_m))

	stop()

	dice_face_s = dotCount()
	print("S: {B}".format(B = dice_face_s))

	if(dice_face_s == dice_face_m):
		seven_seg_turn_on(dice_face_s)
	elif(dice_face_s <= 6 and dice_face_s >= 1):
		seven_seg_turn_on(dice_face_s)
	elif(dice_face_m <= 6 and dice_face_m >= 1):
		seven_seg_turn_on(dice_face_m)
	else:
		print("Dice not found")


	return

def get_dice_report():
	dice_read = dotCount()
	print(dice_read)



#-----------------GYROSCOPE-------------------
"""
Arduino Gyro Code Ahead
"""
def read_gyro_status():
	left.write(b'_')
	right.write(b'_')
	gyro_status_left = read_arduino(LEFT_ARDUINO_ID, no)
	gyro_status_right = read_arduino(RIGHT_ARDUINO_ID, no)
	print("Left Gyro: {A}\tRight Gyro: {B}" \
		.format(A = gyro_status_left, B = gyro_status_right))
	return

def gyro_cali():
	global gyro_is_calibrated

	clear_comm()
	left.write(b'=')
	right.write(b'=')
	left_confirmation = read_arduino(LEFT_ARDUINO_ID, no)
	right_confirmation = read_arduino(RIGHT_ARDUINO_ID, no)
	gyro_is_calibrated = yes
	print("Gyro(s) are Calibrated")
	print("Left:\t{A}\tRight:\t{B}" \
		.format(A = left_confirmation, B = right_confirmation))

	return

def gyro_update_angle():
	clear_comm()
	if(gyro_is_calibrated == no):
		print("Angle was attempted to be read " + \
			"but Gyro has not been Calibrated!")
		return
	left.write(b'?')
	right.write(b'?')

	gyro_angle[LEFT_ARDUINO_ID] = read_arduino(LEFT_ARDUINO_ID, no)
	gyro_angle[RIGHT_ARDUINO_ID] = read_arduino(RIGHT_ARDUINO_ID, no)

	while(len(gyro_angle[LEFT_ARDUINO_ID]) == 0):
		left.write(b'?')
		gyro_angle[LEFT_ARDUINO_ID] = read_arduino(LEFT_ARDUINO_ID,no)
	while(len(gyro_angle[RIGHT_ARDUINO_ID]) == 0):
		right.write(b'?')
		gyro_angle[RIGHT_ARDUINO_ID] = read_arduino(RIGHT_ARDUINO_ID, no)

	print("Left:\t{A}\tRight:{B}". \
		format(A = gyro_angle[LEFT_ARDUINO_ID], \
			B = gyro_angle[RIGHT_ARDUINO_ID]))

	return

def gyro_angle_test():
	while(True):
		gyro_update_angle()

def gyro_report_angle():
	print("Left:\t{A}\tRight:\t{B}". \
		format(A = gyro_angle[LEFT_ARDUINO_ID], \
			B = gyro_angle[RIGHT_ARDUINO_ID]))
	return
def gyro_reset_angle():
	left.write(b',')
	right.write(b',')
	return

#-----------------PID-------------------
def update_PID():
	global gyro_pid_old_output

	gyro_update_angle()

	while(len(gyro_angle[RIGHT_ARDUINO_ID]) == 0):
		print("Right Gyro malfunction")
		gyro_update_angle()

	#used_angle = (gyro_angle[RIGHT_ARDUINO_ID][0] + gyro_angle[LEFT_ARDUINO_ID][0]) / 2
	used_angle = round(gyro_angle[RIGHT_ARDUINO_ID][0])
	gyro_pid.update(used_angle) # for now, use 1 sensor
	result = (gyro_pid.output != gyro_pid_old_output)
	gyro_pid_old_output = gyro_pid.output
	print("PID's OUTPUT: {A}".format(A = gyro_pid.output))
	return result

def obtain_new_motor_speeds(axes, direction, rotation_ratio):
	new_motor_speed = ['100','100','100','100','100']
	#counterclockwise = positive, clockwise = negative
	#motor_set up [left_front, left_back, right_front, right_back]
	y_pos = [1,1,-1,-1]
	y_neg = [-1,-1,1,1]
	x_pos = [1,-1,1,-1]
	x_neg = [-1,1,-1,1]

	y_shift = [y_pos, y_neg]
	x_shift = [x_pos, x_neg]

	overall_shift_factor = [y_shift, x_shift]

	#negative_compensation = []
	#rotation_ratio = gyro_pid.output
	for i in range(len(move_speed[axes][direction])):
		new_motor_speed[i+1] = \
			str(move_speed[axes][direction][i] + \
				overall_shift_factor[axes][direction][i] * 10 * round(rotation_ratio))
	return new_motor_speed

def update_motor_speed(axes,direction,motor_speed):
	print("New Speed: ", end = '')
	print(motor_speed)

	if(axes == Y):
		if(direction == POS_DIRECTION):
			move_forward(motor_speed)
		if(direction == NEG_DIRECTION):
			move_reverse(motor_speed)
	if(axes == X):
		if(direction == POS_DIRECTION):
			move_right(motor_speed)
		if(direction == NEG_DIRECTION):
			move_left(motor_speed)
	return

def gyro_PID_test():
	while(True):

		print(update_PID())
		sleep(0.3)
		new_motor_speed = obtain_new_motor_speeds(Y,POS_DIRECTION, gyro_pid.output)
		update_motor_speed(Y,POS_DIRECTION, new_motor_speed )

	return

def clear_gyro_PID():
	#do the code here
	gyro_pid.clear()
	return

def gyro_PID_rotate():
	#Take the initial value of the gyros and try to match them with the values been received now
	tolerance = 0.5
	print(gyro_pid.output)

	while(gyro_pid.output > 0):
		print("Robot needs to turn ClockWise")
		update_PID()
		sleep(0.1)#Just to be able to read
	while(gyro_pid.output < 0):
		print("Robot needs to turn CounterClock Wise")
		update_PID()
		sleep(0.1)#Just to be able to read
	print("Desired Orientation has been reached")


	return
