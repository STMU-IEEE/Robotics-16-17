

import serial   #This requires Pyserial 3 or later
#import Pathfinding
import sys
import RPi.GPIO as GPIO
import math
from sense_hat import SenseHat
from time import sleep, time
import colorama
from colorama import Fore, Back, Style
from statistics import mean, median, median_low, median_high


GPIO.setmode(GPIO.BCM)

#Setting up the Interrupt
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Setting up communication between arduino and raspberry pi


left_ard='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'
right_ard='/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'
left = serial.Serial(left_ard, 57600)
right = serial.Serial(right_ard, 57600)

#left.timeout = 0.1
#right.timeout = 0.1


FRONT = 1
LEFT = 2
RIGHT = 3
BACK = 4

Y = 0
X = 1

left_arduino = 0
right_arduino = 1

pos_direction = 0
neg_direction = 1

yes = 1
no = 0

cali_pres = 0

encoder_value = [0,0,0,0] #left A, left B, right A, right B

encoder_constant_x = [3246,3382,3246,3155] #value of encoders to reach one block
encoder_constant_y = [2863,2850,2859,2792]

encoder_constant = [encoder_constant_y, encoder_constant_x]

#This are the variables that hold a rough estimate of the speed required to make the robot move straight

move_x_speed_p = [215,190,200,205]
move_x_speed_n = [210,185,210,185]
move_y_speed_p = [165,165,200,200]
move_y_speed_n = [180,180,200,200]

move_x_speed = [move_x_speed_p, move_x_speed_n]
move_y_speed = [move_y_speed_p, move_y_speed_n]

move_speed = [move_y_speed, move_x_speed]

#This are the variables that will be holding the latest recorded values from the capacitive sensor respect to their designation
#Such as wire, iso, and notiso

capacitor_data_wire = [0,0,0,0]#max,median,min,average
capacitor_data_iso = [0,0,0,0]
capacitor_data_notiso = [0,0,0,0]
capacitor_data_constant = [capacitor_data_wire, capacitor_data_notiso, capacitor_data_iso]

capacitor_data_current = [0,0,0,0]#place holder for the newest data from the capacitor sensor

capacitor_block_score = [0,0,0]#This will hold the scores of mutiple data samples from the capacitor_block_identity

term_char = ' '
end_char = '\n'
confirm_char = '@'
emergency_char = '%'


#functions that control the arduino

#-----------------GENERAL PURPOSE-------------------
def assign_side():
    left.write(b'0')
    right.write(b'1')
    return

def read_gyro_status():
	gyro_status_left = read_arduino(left_arduino, no)
	gyro_status_right = read_arduino(right_arduino, no)
	print("Left Gyro: {A}\tRight Gyro: {B}".format(A = gyro_status_left, B = gyro_status_right))
	return

def int_speed(bytes):
	bytes_integer = [0,0,0,0,0]
	for i in range(len(bytes)):
		if i == 0:
			continue
		bytes_integer[i] = eval(bytes[i])
		bytes_integer[i] = int(bytes_integer[i])
		bytes[i] = str( bytes_integer[i] )
	return bytes
"""
def read_integer_serial(terminating_char, side):
	#side if 1 means left and 2 means right
	#term_char separates values
	#end_char ends of transmition

	transmitted_value = 0
	counter = 1
	new_char = 0
	char_is_negative = 1


	while(counter < 15):

		if(side == left_arduino):#Left
			new_char = left.read()
		if(side == right_arduino):#Right
			new_char = right.read()

		#sleep(1)
		#print("Character Received: {A}".format(A = new_char))

		if len(new_char) == 0:
			return -2

		if(new_char == b'\r'):
			#print("Identified b(r)")
			break
		if(new_char == b'\n'):
			#print("Identified b(n)")
			#new_char = terminating_char
			break
		if(new_char == neg_char_b):
			char_is_negative = -1
			continue

		new_char = ord(new_char) - 48

		if new_char == ord(terminating_char) - 48:
			break

		transmitted_value = transmitted_value * 10 + int(new_char)
		counter = counter + 1

	return(transmitted_value * char_is_negative)

def read_integer_serial_long(side,terminating_char):
		#side if 1 means left and 2 means right
	#term_char separates values
	#end_char ends of transmition

	transmitted_value = 0
	counter = 1
	new_char = 0
	char_is_negative = 1


	while(counter < 15):

		if(side == left_arduino):#Left
			new_char = left.read()
		if(side == right_arduino):#Right
			new_char = right.read()

		#sleep(1)
		#print("Character Received: {A}".format(A = new_char))

		if len(new_char) == 0:
			return -2

		if(new_char == b'\r'):
			#print("Identified b(r)")
			break
		if(new_char == b'\n'):
			#print("Identified b(n)")
			#new_char = terminating_char
			break
		if(new_char == neg_char_b):
			char_is_negative = -1
			continue

		new_char = ord(new_char) - 48

		if new_char == ord(terminating_char) - 48:
			break

		transmitted_value = transmitted_value * 10 + int(new_char)
		counter = counter + 1

		if(side == 1):#Left
			left.write(b"@")
		if(side == 2):#Right
			right.write(b"@")

	return(transmitted_value * char_is_negative)
"""
def arduino_data_ready(side_arduino):
	if(side_arduino == left_arduino):
		while(left.in_waiting == 0):
			sleep(0.01)
	if(side_arduino == right_arduino):
		while(right.in_waiting == 0):
			sleep(0.01)
	return True

def read_arduino(side_arduino,with_confirmation):
	#side if 1 means left and 2 means right
	#term_char separates values
	#end_char ends of transmition

	sleep(0.1)
	
	if(side_arduino == left_arduino and arduino_data_ready(left_arduino)):
		bline = left.readline(25)
		if(with_confirmation):
			left.write(confirm_char.encode())
	if(side_arduino == right_arduino and arduino_data_ready(right_arduino)):
		bline = right.readline(25)
		if(with_confirmation):
			right.write(confirm_char.encode())

	print(bline)
	
			
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
	left.flushInput()
	right.flushInput()
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
	return

#Function that occurs when stop and/or start button are pressed

def start_button_pressed(channel):
	#This is where the program to solve the "maze" would go
	#for now it just makes the robot move foward
	restart_comm()
	global cali_pres

	if(cali_pres == 1):
		print("Calibration detected")
		print("Cali_pres returned to 0")
		cali_pres = 0

	return


#-----------------MOVEMENT------------------------
def stop():
	right.write(b"x")
	left.write(b"x")
	return

def move_right(bytes):
	bytes = int_speed(bytes)
	left.write(b"i")
	left.write(bytes[1].encode() )
	left.write(end_char.encode())#separator char
	left.write(bytes[2].encode() )
	left.write(end_char.encode())

	right.write(b"o")
	right.write(bytes[3].encode() )
	right.write(end_char.encode())#separator char
	right.write(bytes[4].encode() )
	right.write(end_char.encode())
	return

def move_left(bytes):
	bytes = int_speed(bytes)
	left.write(b"o")
	left.write(bytes[1].encode() )
	left.write(end_char.encode())#Separator Char
	left.write(bytes[2].encode() )
	left.write(end_char.encode())

	right.write(b"i")
	right.write(bytes[3].encode() )
	right.write(end_char.encode())#Separator Char
	right.write(bytes[4].encode() )
	right.write(end_char.encode())
	return
##LINE 40

def move_forward(bytes):
	bytes = int_speed(bytes)

	print("FORWARD_FUNCTION")
	print(bytes)

	left.write(b"w")
	left.write(bytes[1].encode() )
	left.write(end_char.encode())#Separator Char
	left.write(bytes[2].encode() )
	left.write(end_char.encode())
	#sleep(1)
	right.write(b"w")
	right.write(bytes[3].encode() )
	right.write(end_char.encode())#Separator Char
	right.write(bytes[4].encode() )
	right.write(end_char.encode())
	return

def move_reverse(bytes):
	bytes = int_speed(bytes)
	left.write(b"r")
	left.write(bytes[1].encode() )
	left.write(end_char.encode())#Separator Char
	left.write(bytes[2].encode() )
	left.write(end_char.encode())

	right.write(b"r")
	right.write(bytes[3].encode() )
	right.write(end_char.encode())#Separator Char
	right.write(bytes[4].encode() )
	right.write(end_char.encode())
	return

def rotate_counter(bytes):
	#counter clockwise --> left reverse, right forward
	bytes = int_speed(bytes)
	left.write(b"r")
	left.write(bytes[1].encode() )
	left.write(end_char.encode())
	left.write(bytes[1].encode() )
	left.write(end_char.encode())

	right.write(b"w")
	right.write(bytes[1].encode() )
	right.write(end_char.encode())
	right.write(bytes[1].encode() )
	right.write(end_char.encode())
	return

def rotate_clockwise(bytes):
	#counter clockwise --> left forward, right reverse
	bytes = int_speed(bytes)
	left.write(b"w")
	left.write(bytes[1].encode() )
	left.write(end_char.encode())
	left.write(bytes[1].encode() )
	left.write(end_char.encode())

	right.write(b"r")
	right.write(bytes[1].encode() )
	right.write(end_char.encode())
	right.write(bytes[1].encode() )
	right.write(end_char.encode())

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

		sleep(1)

		print("Beginning test {A}".format(A = i+1))

		cali_pres = 1

		bytes = ['@','@', '@', '@', '@']
		bytes[1] = str( 250 )
		bytes[2] = str( 250 )
		bytes[3] = str( 250 )
		bytes[4] = str( 250 )

		#print("250 to all motors")


		if(axes == Y):#Y Calibration
			for i in range(4):
				print("Motor speed changed to Y+ default")
				bytes[i + 1] = str(move_y_speed_p[i])
			move_forward(bytes)
		if(axes == X):#X Calibration
			for i in range(4):
				print("Motor speed changed to X+ default")
				bytes[i + 1] = str(move_x_speed_p[i])
			move_right(bytes)

		sleep(1)

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

	clear_comm()

	left.write(b"m")
	right.write(b"m")

	global encoder_value
	encoder_holder = read_arduino(left_arduino, no)
	
	encoder_value[0] = encoder_holder[0]
	encoder_value[1] = encoder_holder[1]

	encoder_holder = read_arduino(right_arduino, no)
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
	print("Left A: {A1} B: {B1} Right A: {A2} B: {B2}".format(A1 = encoder_value[0], B1 = encoder_value[1],A2 = encoder_value[2], B2 = encoder_value[3] ) )

	return


def encoder_constant_value():
	print("Constant values of Encoders")
	print("Encoder Values for Y Axis")
	print("Left A: {A1} B: {B1} Right A: {A2} B: {B2}".format(A1 = encoder_constant_y[0], B1 = encoder_constant_y[1],A2 = encoder_constant_y[2], B2 = encoder_constant_y[3] ) )
	print("Encoder Values for X Axis")
	print("Left A: {A1} B: {B1} Right A: {A2} B: {B2}".format(A1 = encoder_constant_x[0], B1 = encoder_constant_x[1],A2 = encoder_constant_x[2], B2 = encoder_constant_x[3] ) )
	return

def encoder_completion(axes):
	"""
	completion = 0
	if(axes == 0):#Y
		for i in range(4):
			if(int(encoder_value[i]) >= average(encoder_constant_y)):
				completion = completion + 1

	if(axes == 1):#X
		for i in range(4):
			if(int(encoder_value[i]) >= average(encoder_constant_x)):
				completion = completion + 1
	"""
	completion = 0
	for i in range(4):
		if(int(encoder_value[i]) >= mean(encoder_constant[axes])):
			completion = completion + 1

	if(completion >= 4):
		return 1

	return 0

def move_y(direction, speed):
	direction = int(direction)
	print("Axes: Y Side:{A} Speed: {B}".format(A = direction, B = speed))

	encoder_reset()
	bytes = ['$','$', '$', '$', '$']

	bytes[1] = str( speed )
	bytes[2] = str( int(speed))
	bytes[3] = str( speed )
	bytes[4] = str( speed )

	for i in range(4):
		bytes[i+1] = str(move_y_speed[direction][i])

	if(direction == pos_direction):
		move_forward(bytes)
	if(direction == neg_direction):
		move_reverse(bytes)

	#encoder_constant_value()
	counter = 0
	while(encoder_completion(Y) == 0): #if the function returns 0, that means that non of the encoders have reach the desired value
		if(counter >= 30):
			print(".", end = '')
			counter = 0
		counter = counter + 1
		encoder_update()
		sleep(0.01)
	stop()

	return

def move_x(direction, speed):
	direction = int(direction)
	print("Axes: X Side:{A} Speed: {B}".format(A = direction, B = speed))

	encoder_reset()
	bytes = ['@','@', '@', '@', '@']

	bytes[1] = str( speed )
	bytes[2] = str( speed )
	bytes[3] = str( speed )
	bytes[4] = str( speed )

	for i in range(4):
		bytes[i+1] = str(move_x_speed[direction][i])

	if(direction == pos_direction):
		move_right(bytes)
	if(direction == neg_direction):
		move_left(bytes)


	#encoder_constant_value()
	counter = 0
	while(encoder_completion(X) == 0): #if the function returns 0, that means that non of the encoders have reach the desired value
		if(counter >= 30):
			print(".", end = '')
			counter = 0
		counter = counter + 1
		encoder_update()
		sleep(0.01)
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

		"""
		sensor_collect[0] = read_arduino(left_arduino, 0)#1 means left, 2 means right
		while(sensor_collect[0] == -2):
			clear_comm()
			left.write(b"u")
			sensor_collect[0] = read_arduino(left_arduino, 0)

		sensor_collect[1] = read_arduino(left_arduino, 0)
		while(sensor_collect[1] == -2):
			clear_comm()
			left.write(b"u")
			trash_value = read_arduino(left_arduino, 0)
			sensor_collect[1] = read_arduino(left_arduino, 0)

		sensor_collect[2] = read_arduino(right_arduino, 0)
		while(sensor_collect[2] == -2):
			clear_comm()
			right.write(b"u")
			sensor_collect[2] = read_arduino(right_arduino, 0)

		sensor_collect[3] = read_arduino(right_arduino, 0)
		while(sensor_collect[3] == -2):
			clear_comm()
			right.write(b"u")
			trash_value = read_arduino(right_arduino, 0)
			sensor_collect[3] = read_arduino(right_arduino, 0)
		"""

		left.write(b"u")
		right.write(b"u")

		sensor_holder_left = read_arduino(left_arduino,no)
		sensor_holder_right = read_arduino(right_arduino,no)
		
		if(len(sensor_holder_left) < 2 and len(sensor_holder_right) < 2):
			print("*")
			continue
		
		actual_sensor_collect_fre += 1
		sensor_collect = sensor_holder_left + sensor_holder_right

		for i in range(4):
			if(sensor_collect[i] == 0):
				sensor_collect[i] = 200
					

		sensor_total[0] += sensor_collect[0]
		sensor_total[1] += sensor_collect[1]

		sensor_total[2] += sensor_collect[2]
		sensor_total[3] += sensor_collect[3]


	left_back_ave = sensor_total[0] / actual_sensor_collect_fre
	left_left_ave = sensor_total[1] / actual_sensor_collect_fre

	right_front_ave = sensor_total[2] / actual_sensor_collect_fre
	right_right_ave = sensor_total[3] / actual_sensor_collect_fre


	print("LEFT: B:{B}	L:{L}	RIGHT: F:{F}	R:{R}".format(B = left_back_ave,L = left_left_ave,F = right_front_ave, R = right_right_ave) )

	# North 1000
	# South  100
	# East    10
	# West     1

	ultra_ave = [right_front_ave, left_back_ave, right_right_ave, left_left_ave]

	block_direction = [0,0,0,0]
	
	block_message = 0
	for i in range(4):
		if(ultra_ave[i] <= 8):
			block_direction[i] = 1

	#print(block_direction)
	for i in range(4):
		if(block_direction[i] == 1):
			block_message = block_message + pow(10,3-i)

	#print("Block Message: ", end = '')
	#print(block_message)
	
	print("Block Direction : ", end = '')

	return block_direction

#-----------------CAPACITOR-------------------

def capacitor_sensor():
	#The right arduino is the only arduino with a capacitive sensor
	capacitor_hard_reset()
	sensor_data = [-2,-2,-2,-2] #Highest, median, lowest, average
	clear_comm()
	flag = 0

	print("Collecting data from Capacitive Sensor")

	for i in range(20):#This is the amount of attempts the Raspberry has to recieve the information
		flag = 0
		clear_comm()
		right.write(b"C")
		#sleep(0.5)
		capacitor_hard_reset()
		"""
		sensor_data[0] = read_arduino(right_arduino, 1)
		print(sensor_data[0])
		sensor_data[1] = read_arduino(right_arduino, 1)
		print(sensor_data[1])
		sensor_data[2] = read_arduino(right_arduino, 1)
		print(sensor_data[2])
		sensor_data[3] = read_arduino(right_arduino, 1)
		print(sensor_data[3])
		"""
		sensor_data = read_arduino(right_arduino, yes)
		print(sensor_data)

		if(len(sensor_data) == 0):
			continue

		for i in range(len(sensor_data)):#If any of the values is a trash value
			if(sensor_data[i] < 10000 and sensor_data[i] > -2):#To small
				#print("Trash Value Detected: Cut off")
				print("C, ", end = '')
				flag = 1
				continue
			if(sensor_data[i] > 100000):#To big
				#print("Trash Value Detected: Run on")
				print("R, ", end = '')
				flag = 1
				continue
			if(sensor_data[i] == -2):
				#print("Communication Failure")
				print("F, ", end = '')
				flag = 1
				continue
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
		capacitor_data_current[i] = sensor_data[i]

	clear_comm()
	return

def capacitor_report():
	print("Value of Capacitor Data Current now: ", end = '')
	print(capacitor_data_current)
	return

def capacitor_hard_reset():
	right.write(b"H")
	print("Capacitor sensor reset")
	#This lets the capacitor reset
	return

def capacitor_trash_value():
	flag = False
	for i in range(4):
		if(capacitor_data_current[i] > 100000 or capacitor_data_current[i] < 10000 or capacitor_data_current[i] == -2):
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
	"""
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

		if(i == 0):#Wire test
			for j in range(4):
				capacitor_data_wire[j] = capacitor_data_current[j]

		if(i == 1):#Not Isolated with no wire
			for j in range(4):
				capacitor_data_notiso[j] = capacitor_data_current[j]

		if(i == 2):#Isolated
			for j in range(4):
				capacitor_data_iso[j] = capacitor_data_current[j]
	"""
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

def capacitor_calibrate_update(block_calibrate):

	print("Updating Block Data")
	print("Before update Calibrate")

	print(capacitor_data_constant[block_calibrate])

	for u in range(4):
		capacitor_data_constant[block_calibrate][u] = round((capacitor_data_current[u] + capacitor_data_constant[block_calibrate][u])/2)

	print("After update Calibrate")

	print(capacitor_data_constant[block_calibrate])

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

	"""
	for p in range(3):
		if(diff_rating[p] == 2):
			tied_check = tied_check + 1
	if(tied_check == 2):
		print("WARNING")
		print("Tied in sensor catorgories")
		print("Recommended to retake the values")
		block_identity_message = -1
	"""
	#only recalibrate if difference between values is not too big


	for j in range(4):
		if(diff_holder[j] > diff_tolerance):
			diff_overpass_tolerace = 1

	if(diff_overpass_tolerance == 0 and diff_rating[block_identity_message] == 7):
		 capacitor_calibrate_update(block_identity_message)
	else:
		print("Diff Tolerance is surpassed or/and diff_rating is not equal to 7")

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

	return block_identity_message

#-----------------SERVOS-------------------

def servo_top(servo_location):
	servo_location = int(servo_location)

	if servo_location == FRONT:
		right.write(b"t")
	if servo_location == BACK:
		left.write(b"t")
	return

def servo_bottom(servo_location):
	servo_location = int(servo_location)

	if servo_location == FRONT:
		right.write(b"b")
	if servo_location == BACK:
		left.write(b"b")
	return

def servo_change(bytes):
	#bytes[1] = servoH_top
	#bytes[2] = servoH_bottom
	#Sending bytes to the left arduino
	left.write(bytes[0].encode() )
	left.write(bytes[1].encode() )
	left.write(end_char.encode())#Separator Char
	left.write(bytes[2].encode() )
	left.write(end_char.encode())
	#Sending bytes to the right arduino
	right.write(bytes[0].encode() )
	right.write(bytes[1].encode() )
	right.write(end_char.encode())#Separator Char
	right.write(bytes[2].encode() )
	right.write(end_char.encode())
	return

def servo_info():
	left.write(b"n")
	right.write(b"n")
	
	servo_holder = read_arduino(left_arduino, no)
	
	left_servo_position = servo_holder[0]
	left_servo_height_top = servo_holder[1]
	left_servo_height_bottom = servo_holder[2]

	servo_holder = read_arduino(right_arduino , no)
	
	right_servo_position = servo_holder[0]
	right_servo_height_top = servo_holder[1]
	right_servo_height_bottom = servo_holder[2]

	print("Left Servo Information:")
	print("Position: {P} Height Top: {T} Height Bottom: {B}".format(P = left_servo_position, T = left_servo_height_top, B = left_servo_height_bottom) )
	print("Right Servo Information:")
	print("Position: {P} Height Top: {T} Height Bottom: {B}".format(P = right_servo_position, T = right_servo_height_top, B = right_servo_height_bottom) )

#Assigned the interrupt their functions
GPIO.add_event_detect(26, GPIO.RISING, callback = start_button_pressed, bouncetime = 300)


"""Raspberry Gyro Code Ahead


Information Here
positive increase means clockwise rotation
negative increase means counter-clockwise rotation

Direction is reference with the following numbers

					1
					^
					|
					|

       fro_left []----[] fro_right
		|  w   |
       2<---    | a  d |    --->3
		|   s  |
       bac_left []----[] bac_right

					|
					|
					V
					4



#Setting up gyro sensitive variables [defaults]
sense = SenseHat()

FRONT_LEFT = "front_left"
FRONT_RIGHT = "front_right"
BACK_LEFT = "back_left"
BACK_RIGHT = "back_right"

pre_value = 0
new_value = 0


motor_speed = {'front_left': 255, 'front_right': 255, 'back_left': 255, 'back_right': 255}
motor_change = [0,0,0,0]

direction = 0
max_speed = 250
sensativity = 1
fre = 10
diff = 0
fix_bias = 15
lowest_speed = 70
gyro_raw = 0


def get_gyro_reading():

	global gyro_raw

	motion = sense.get_gyroscope()
	gyro_raw = motion["yaw"] - 180
	return gyro_raw #change gyro reading system from 0 - 360 to -180 - 180


def ave_gyro():
	total = 0
	for i in range(fre):
		new_value_raw = get_gyro_reading()
		total = total + new_value_raw
		sleep(0.02)
	ave = total / (fre)
	return ave

def update_diff():
	global new_value
	global diff

	new_value = ave_gyro()
	diff = new_value - pre_value

	if abs(diff) > 182:#If the gyro value passes the 180 -180 border
		diff = 360 - (abs (pre_value) + abs(new_value) )
	return

def rotate_counter_gyro():
	inital_diff = 0
	pre_fre = fre

	for i in range(3):
		update_diff()

	redefine_fre(20)
	print(diff)
	inital_diff = diff

	while(abs(diff) > sensativity + 1):
		update_diff()
		print(diff)

		if abs(diff) > sensativity * 10:
			rotation_speed = 150
		if abs(diff) > sensativity * 9:
			rotation_speed = 120
		if abs(diff) > sensativity * 8:
			rotation_speed = 100
		if abs(diff) > sensativity * 7:
			rotation_speed = 90
		if abs(diff) > sensativity * 6:
			rotation_speed = 80
		if abs(diff) > sensativity * 5:
			rotation_speed = 75
		if abs(diff) > sensativity * 4:
			rotation_speed = 70
		if abs(diff) > sensativity * 3:
			rotation_speed = 60
		else:
			rotation_speed = 60

		if(abs(diff) > abs(inital_diff) + 10):
			stop()
			rotate_clockwise_gyro()
			return

		rotation_speed = round(rotation_speed)
		rotation_comm = ['@','@']
		rotation_comm[1] = str(rotation_speed)
		rotate_counter(rotation_comm)

	redefine_fre(pre_fre)
	stop()
	return

def rotate_clockwise_gyro():
	pre_fre = fre

	for i in range(3):
		update_diff()

	redefine_fre(20)
	print(diff)
	inital_diff = diff

	while(abs(diff) > sensativity + 1):
		update_diff()
		print(diff)

		if abs(diff) > sensativity * 10:
			rotation_speed = 150
		if abs(diff) > sensativity * 9:
			rotation_speed = 120
		if abs(diff) > sensativity * 8:
			rotation_speed = 100
		if abs(diff) > sensativity * 7:
			rotation_speed = 97
		if abs(diff) > sensativity * 6:
			rotation_speed = 95
		if abs(diff) > sensativity * 5:
			rotation_speed = 90
		if abs(diff) > sensativity * 4:
			rotation_speed = 85
		if abs(diff) > sensativity * 3:
			rotation_speed = 80
		else:
			rotation_speed = 60

		if(abs(diff) > abs(inital_diff) + 10):
			stop()
			rotate_counter_gyro()
			return

		rotation_speed = round(rotation_speed)
		rotation_comm = ['@','@']
		rotation_comm[1] = str(rotation_speed)
		rotate_clockwise(rotation_comm)

	redefine_fre(pre_fre)
	stop()
	return



#creates the new motor speeds to correct leaning
def change_speed():
	largest_value = 0
	factor = 1

	global motor_speed
	global diff
	global motor_speed


	if abs(diff) < sensativity:
		print("Going straight")
		print("Difference of {diffe}".format(diffe = str(diff) ) )
		if motor_speed[FRONT_LEFT] > largest_value:
			largest_value = motor_speed[FRONT_LEFT]
		if motor_speed[BACK_LEFT] > largest_value:
			largest_value = motor_speed[BACK_LEFT]
		if motor_speed[FRONT_RIGHT] > largest_value:
			largest_value = motor_speed[FRONT_RIGHT]
		if motor_speed[BACK_RIGHT] > largest_value:
			largest_value = motor_speed[BACK_RIGHT]

		motor_speed[FRONT_LEFT] = largest_value + 5
		motor_speed[FRONT_RIGHT] = largest_value + 5
		motor_speed[BACK_LEFT] = largest_value + 5
		motor_speed[BACK_RIGHT] = largest_value + 5

		motor_change[0] = 0
		motor_change[1] = 0
		motor_change[2] = 0
		motor_change[3] = 0

	if diff > sensativity and diff < 50:
		print("Clockwise and go")
		print("Difference of {diffe}".format(diffe = str(diff)))

		if direction == FRONT:

			if motor_speed[FRONT_RIGHT] + abs(diff) < max_speed and motor_speed[FRONT_RIGHT] + abs(diff) < max_speed:
				motor_speed[FRONT_RIGHT] += abs(diff) * factor
				motor_speed[BACK_RIGHT] += abs(diff) * factor

				motor_change[0] = 0
				motor_change[1] = 0
				motor_change[2] = 1
				motor_change[3] = 1

			else:
				motor_speed[FRONT_LEFT] -= abs(diff) * factor
				motor_speed[BACK_LEFT] -= abs(diff) * factor

				motor_change[2] = 0
				motor_change[3] = 0
				motor_change[0] = 2
				motor_change[1] = 2
		if direction == RIGHT:
			print("HelloR")
		if direction == LEFT:
			print("HelloL")
		if direction == BACK:
			print("HelloB")

	if diff > sensativity and diff > 50:
		print("Clockwise and stop")

		rotate_counter_gyro()

		motor_change[2] = 3
		motor_change[3] = 3
		motor_change[0] = 3
		motor_change[1] = 3

		stop()

	if diff < (sensativity * -1) and diff > -50:
		print("Counter-ClockWise and go")
		print("Difference of {diffe}".format(diffe = str(diff) ) )

		if direction == FRONT:

			if motor_speed[FRONT_LEFT] + abs(diff) < max_speed and motor_speed[BACK_LEFT] + abs(diff) < max_speed:
				motor_speed[FRONT_LEFT] += abs(diff) * factor
				motor_speed[BACK_LEFT] += abs(diff) * factor

				motor_change[2] = 0
				motor_change[3] = 0
				motor_change[0] = 1
				motor_change[1] = 1

			else:
				motor_speed[FRONT_RIGHT] -= abs(diff) * factor
				motor_speed[BACK_RIGHT] -= abs(diff) * factor

				motor_change[0] = 0
				motor_change[1] = 0
				motor_change[2] = 2
				motor_change[3] = 2

		if direction == RIGHT:
			print("HelloR")
		if direction == LEFT:
			print("HelloL")
		if direction == BACK:
			print("HelloB")

	if diff < (sensativity * -1) and diff < -50:
		print("Counter-ClockWise and stop")

		rotate_clockwise_gyro()

		motor_change[2] = 3
		motor_change[3] = 3
		motor_change[0] = 3
		motor_change[1] = 3

		stop()

	return

def speed_constraint():
	global motor_speed
	#speed Restrictions

	if motor_speed[FRONT_LEFT] > max_speed:
		motor_speed[FRONT_LEFT] = max_speed
	if motor_speed[FRONT_LEFT] < lowest_speed:
		motor_speed[FRONT_LEFT] = lowest_speed

	if motor_speed[FRONT_RIGHT] > max_speed:
		motor_speed[FRONT_RIGHT] = max_speed
	if motor_speed[FRONT_RIGHT] < lowest_speed:
		motor_speed[FRONT_RIGHT] = lowest_speed

	if motor_speed[BACK_LEFT] > max_speed - fix_bias:
		motor_speed[BACK_LEFT] = max_speed - fix_bias
	if motor_speed[BACK_LEFT] < lowest_speed - fix_bias :
		motor_speed[BACK_LEFT] = lowest_speed - fix_bias

	if motor_speed[BACK_RIGHT] > max_speed:
		motor_speed[BACK_RIGHT] = max_speed
	if motor_speed[BACK_RIGHT] < lowest_speed:
		motor_speed[BACK_RIGHT] = lowest_speed
	return

def speed_display():
	#1 means green, 2 means red and 0 means white
	#printing the speeds with the corresponding color
	if motor_change[0] == 1: #green
		print(Fore.GREEN + ' {f_L} '.format(f_L = str(motor_speed[FRONT_LEFT])), end = "" )
	if motor_change[0] == 2: #red
		print(Fore.RED + ' {f_L} '.format(f_L = str(motor_speed[FRONT_LEFT])), end = "" )
	if motor_change[0] == 0: #white
		print(Style.RESET_ALL + ' {f_L} '.format(f_L = str(motor_speed[FRONT_LEFT])), end = "" )
	if motor_change[0] == 3: #yellow for rotation
		print(Fore.YELLOW + ' {f_L} '.format(f_L = str(motor_speed[FRONT_LEFT])), end = "" )


	if motor_change[2] == 1: #green
		print(Fore.GREEN + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )
	if motor_change[2] == 2: #red
		print(Fore.RED + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )
	if motor_change[2] == 0: #white
		print(Style.RESET_ALL + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )
	if motor_change[2] == 3: #yellow
		print(Fore.YELLOW + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )

	print("\n")

	if motor_change[1] == 1: #green
		print(Fore.GREEN + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )
	if motor_change[1] == 2: #red
		print(Fore.RED + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )
	if motor_change[1] == 0: #white
		print(Style.RESET_ALL + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )
	if motor_change[1] == 3: #yellow
		print(Fore.YELLOW + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )

	if motor_change[3] == 1: #green
		print(Fore.GREEN + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )
	if motor_change[3] == 2: #red
		print(Fore.RED + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )
	if motor_change[3] == 0: #white
		print(Style.RESET_ALL + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )
	if motor_change[3] == 3: #yellow
		print(Fore.YELLOW + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )

	print(Style.RESET_ALL + "\n")
	return


def send_speed():
	bytes = ['@','@', '@', '@', '@']
	bytes[1] = str( round( motor_speed[FRONT_LEFT] ) )
	bytes[2] = str( round( motor_speed[BACK_LEFT] - fix_bias ) )
	bytes[3] = str( round( motor_speed[FRONT_RIGHT] ) )
	bytes[4] = str( round( motor_speed[BACK_RIGHT] ) )

	print(bytes)

	if direction == FRONT:
		move_forward(bytes)
	if direction == LEFT:
		move_left(bytes)
	if direction == RIGHT:
		move_right(bytes)
	if direction == BACK:
		move_reverse(bytes)

	return

def rotation():
	A = ave_gyro()
	B = ave_gyro()
	if B - A > 0.6:
		print("ClockWise: {diff}".format(diff = (B-A) ) )
	if B - A < -0.6:
		print("CounterClockWise: {diff}".format(diff = (B-A) ) )
	if abs( B - A ) <  0.6 :
		print("Stationary")

def move_gyro(direct, starting_speed, sense_gyro):
	#Code to make the robot move straight
	global sensativity
	global motor_speed
	global max_speed
	global direction

	sensativity = int(sense_gyro)

	motor_speed[FRONT_LEFT] = int(starting_speed)
	motor_speed[BACK_LEFT] = int(starting_speed)
	motor_speed[FRONT_RIGHT] = int(starting_speed)
	motor_speed[BACK_RIGHT] = int(starting_speed)

	max_speed = int(starting_speed)

	direction = direct#making a local variable a global variable

	for j in range(3):#makig sure that the sensor works
		redefine_pre()


	while(True):
		update_diff()
		change_speed()
		speed_constraint()
		speed_display()
		#send_speed()
	return


def gyro_main():
	global direction
	direction = 1
	for i in range(20):
		#send_speed()
		sleep(0.5)
		update_diff()
		print("Pre: {P} New: {N} Diff: {D}".format(P = pre_value,N = new_value, D = diff))
		#print(get_gyro_reading() )
	return

def redefine_pre():
	global pre_value
	for i in range(4):
		pre_value  = ave_gyro()
	print("Now the value of Pre is {Pre}".format(Pre = pre_value) )
	return

def redefine_fre(new_value_fre):
	global fre
	fre = int(new_value_fre)
	print("Now the value of fre is {FRE}". format(FRE = fre) )
	return

def redefine_sensa(new_value_sen):
	global sensativity
	sensativity = int(new_value_sen)
	print("Now the value of sensativity is {SE}".format(SE = sensativity) )
	return

def north():
	north = sense.get_compass()
	print("North: %s" % north)
	return

"""

"""
Arduino Gyro Code Ahead
"""

gyro_angle = [0,0] #Left, Right
gyro_cali_b = b'='
gyro_update_angle_b = b'?'

def gyro_cali():
	clear_comm()
	left.write(b'=')
	right.write(b'=')
	left_confirmation = read_arduino(left_arduino, no)
	right_confirmation = read_arduino(right_arduino, no)
	print("Left:\t{A}\tRight:\t{B}".format(A = left_confirmation, B = right_confirmation))

	return

def gyro_update_angle():
	clear_comm()
	left.write(b'?')
	right.write(b'?')

	gyro_angle[left_arduino] = read_arduino(left_arduino, no)
	gyro_angle[right_arduino] = read_arduino(right_arduino, no)

	return

def gyro_report_angle():
	print("Left:\t{A}\tRight:\t{B}".format(A = gyro_angle[left_arduino], B = gyro_angle[right_arduino]))
	return

"""
def fix_direction():
	
"""
