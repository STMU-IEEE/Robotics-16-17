\
#Hello this is Nick and Eduardo 
import serial
#import Pathfinding
import sys
import RPi.GPIO as GPIO
import math 
from sense_hat import SenseHat
from time import sleep, time
import colorama 
from colorama import Fore, Back, Style
 

GPIO.setmode(GPIO.BCM)

#Setting up the Interrupt
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Setting up communication between arduino and raspberry pi

 
left_ard='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'
right_ard='/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'
left = serial.Serial(left_ard, 9600)
right = serial.Serial(right_ard, 9600)

left.timeout = 0.1
right.timeout = 0.1


FRONT = 1
LEFT = 2
RIGHT = 3
BACK = 4

cali_pres = 0

""" Time dependent System
time_distance_slope = {'y':-0.014,'x':-0.018418}
time_distance_shift = {'y':7.15,'x':8.77567}
"""
encoder_value = [0,0,0,0] #left A, left B, right A, right B


encoder_constant_x = [15,15,15,15] #value of encoders to reach one block
encoder_constant_y = [14,14,14,14]

move_x_speed_p = [215,190,200,205]
move_x_speed_n = [210,185,210,185]
move_y_speed_p = [165,165,200,200]
move_y_speed_n = [180,180,200,200]
 

#functions that control the arduino
def int_speed(bytes):
	bytes_integer = [0,0,0,0,0]
	for i in range(len(bytes)):
		if i == 0:
			continue
		bytes_integer[i] = eval(bytes[i])
		bytes_integer[i] = int(bytes_integer[i])
		bytes[i] = str( bytes_integer[i] )
	return bytes

def read_integer_serial(terminating_char, side):
	#side if 1 means left and 2 means right
	#'-' separates values
	#'&' ends of transmition
	char_read = [-1,-1,-1,-1]
	if side == 1:#left
		#print("left")
		for i in range(4):#Read the char and end if read char is the terminating_char
			new_char = left.read()
			if len(new_char) == 0:
				#print("Left Ultrasonic Failure")
				return -2
			new_char = ord(new_char) - 48 #- will return -3, & will return -8
			#print("Read Char: {I}".format(I = new_char) )
			if new_char == ord(terminating_char) - 48:
				#print("Read terminating char")
				break
			char_read[i] = new_char

		if char_read[0] == -1:
			return 0
		elif char_read[1] == -1:
			return int(char_read[0])
		elif char_read[2] == -1:
			return int(char_read[0]) * 10 + int( char_read[1] )
		elif char_read[3] == -1:
			return int(char_read[0]) * 100  + int( char_read[1] ) * 10  + int( char_read[2] )
		else:
			return int(char_read[0]) * 1000 + int( char_read[1] ) * 100 + int( char_read[2] ) * 10 + int( char_read[3] ) 

	if side == 2:#right
		#print("right")
		for i in range(4):#Read the char and end if read char is the terminating_char
			new_char = right.read()
			if len(new_char) == 0:
				#print("Right Ultrasonic Failure")
				return -2

			new_char = ord(new_char) - 48
			#print("Read Char: {I}".format(I = new_char) )
			if new_char == ord(terminating_char) - 48:
				#print("Read terminating Char")
				break
			char_read[i] = new_char

		if char_read[0] == -1:
			return 0
		elif char_read[1] == -1:
			return int(char_read[0])
		elif char_read[2] == -1:
			return int(char_read[0]) * 10  + int( char_read[1] )
		elif char_read[3] == -1:
			return int(char_read[0]) * 100  + int( char_read[1] ) * 10 + int( char_read[2] )
		else:
			return int(char_read[0]) * 1000 + int( char_read[1] ) * 100 + int( char_read[2] ) * 10 + int( char_read[3] )


def end():
	"Stops the motors and disconnects the serial comm channels."##LINE 20
	stop()
	right.close()
	left.close()
	return
def clear_comm():
	left.flushInput()
	right.flushInput()

def stop():
	right.write(b"x")
	left.write(b"x")
	return

def move_right(bytes):
	bytes = int_speed(bytes)
	left.write(b"i")
	left.write(bytes[1].encode() )
	left.write(b"&")#separator char
	left.write(bytes[2].encode() )
	left.write(b"&")

	right.write(b"o")
	right.write(bytes[3].encode() )
	right.write(b"&")#separator char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return

def move_left(bytes):
	bytes = int_speed(bytes)
	left.write(b"o")
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )
	left.write(b"&")

	right.write(b"i")
	right.write(bytes[3].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return
##LINE 40

def move_forward(bytes):
	bytes = int_speed(bytes)
	
	print("FORWARD_FUNCTION")
	print(bytes)

	left.write(b"w")
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )
	left.write(b"&")
	#sleep(1)
	right.write(b"w")
	right.write(bytes[3].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return

def move_reverse(bytes):
	bytes = int_speed(bytes)
	left.write(b"r")
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )
	left.write(b"&")

	right.write(b"r")
	right.write(bytes[3].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return

def rotate_counter(bytes):
	#counter clockwise --> left reverse, right forward
	bytes = int_speed(bytes)
	left.write(b"r")
	left.write(bytes[1].encode() )
	left.write(b"&")
	left.write(bytes[1].encode() )
	left.write(b"&")
	
	right.write(b"w")
	right.write(bytes[1].encode() )
	right.write(b"&")
	right.write(bytes[1].encode() )
	right.write(b"&")
	return
	
def rotate_clockwise(bytes):
	#counter clockwise --> left forward, right reverse
	bytes = int_speed(bytes)
	left.write(b"w")
	left.write(bytes[1].encode() )
	left.write(b"&")
	left.write(bytes[1].encode() )
	left.write(b"&")
	
	right.write(b"r")
	right.write(bytes[1].encode() )
	right.write(b"&")
	right.write(bytes[1].encode() )
	right.write(b"&")
	
	return

def encoder_update():#1 for Y, 2 for X
	clear_comm()
	left.write(b"m")
	right.write(b"m")

	global encoder_value
	
	encoder_value[0] = read_integer_serial('-',1)#A1
	encoder_value[1] = read_integer_serial('&',1)#B1

	encoder_value[2] = read_integer_serial('-',2)#A2
	encoder_value[3] = read_integer_serial('&',2)#B2

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

def average(list):
	total = 0
	for i in range(len(list)):
		total = total + list[i]
	return round( total / len(list) )

def encoder_completion(axes):

	completion = 0 
	if(axes == 1):#Y
		for i in range(4):
			if(int(encoder_value[i]) >= average(encoder_constant_y)):
				completion = completion + 1

	if(axes == 2):#X
		for i in range(4):
			if(int(encoder_value[i]) >= average(encoder_constant_x)):
				completion = completion + 1	
	
	if(completion >= 3):
		return 1

	return 0

def move_y(side, speed):
	side = int(side)
	print("Axes: Y Side:{A} Speed: {B}".format(A = side, B = speed)) 

	encoder_reset()
	bytes = ['@','@', '@', '@', '@']
	
	bytes[1] = str( speed )
	bytes[2] = str( int(speed))
	bytes[3] = str( speed )
	bytes[4] = str( speed )

	if(int(speed) == 1):
		if(side == 1):
			for i in range(4):
				bytes[i + 1] = str(move_y_speed_p[i])
			move_forward(bytes)
			print("Forward")
		if(side == 2):
			for i in range(4):
				bytes[i + 1] = str(move_y_speed_n[i])
			move_reverse(bytes)
			print("Backward")

	if(side == 1 and int(speed) != 1):
		move_forward(bytes)
	if(side == 2 and int(speed) != 1):
		move_reverse(bytes)

	#encoder_constant_value()
	counter = 0
	while(encoder_completion(1) == 0): #if the function returns 0, that means that non of the encoders have reach the desired value
		if(counter >= 30):
			print(".", end = '')
			counter = 0
		counter = counter + 1
		encoder_update()
		sleep(0.01)
	stop()


	
	""" Time dependent System
	time_interval = time_distance_function(int(speed),1) * block
	print("time interval given per block: {A}".format(A = time_interval))
	
	before_mov = time()
	
	future_mov = before_mov + time_interval 
	
	if(side == FRONT):
		move_forward(bytes)
	if(side == BACK):
		move_reverse(bytes)
	while(time() < future_mov):
		sleep(0.001)
	stop()
	"""

	return
	
def move_x(side, speed):
	side = int(side)
	print("Axes: X Side:{A} Speed: {B}".format(A = side, B = speed)) 

	encoder_reset()
	bytes = ['@','@', '@', '@', '@']
	
	bytes[1] = str( speed )
	bytes[2] = str( speed)
	bytes[3] = str( speed )
	bytes[4] = str( speed )
	
	if(int(speed) == 1):
		if(side == 1):
			for i in range(4):
				bytes[i + 1] = str(move_x_speed_p[i])
			move_right(bytes)
			print("Right")
		if(side == 2):
			for i in range(4):
				bytes[i + 1] = str(move_x_speed_n[i])
			move_left(bytes)
			print("Left")
	if(side == 1 and int(speed) != 1):
		move_right(bytes)
	if(side == 2 and int(speed) != 1):
		move_left(bytes)

	#encoder_constant_value()
	counter = 0
	while(encoder_completion(2) == 0): #if the function returns 0, that means that non of the encoders have reach the desired value
		if(counter >= 30):
			print(".", end = '')
			counter = 0
		counter = counter + 1
		encoder_update()
		sleep(0.01)
	stop()

	""" Time dependent system
	time_interval = time_distance_function(int(speed),2) * block
	
	before_mov = time()
	
	future_mov = before_mov + time_interval 
	print("time interval given per block: {B}".format(B = time_interval) )
	
	if(side == LEFT):
		move_left(bytes)
	if(side == RIGHT):
		move_right(bytes)
		
	while(time() < future_mov):
		sleep(0.001)
	stop()

	"""
	
	return


def us_sensor():
	sensor_collect_fre = 5
	clear_comm()
	left.write(b"u")
	right.write(b"u")

	sensor_total = [0,0,0,0]#left_back, left_left, right_front, right_right
	sensor_collect = [0,0,0,0]
	trash_value = 0

	for i in range(sensor_collect_fre):
	
		sensor_collect[0] = read_integer_serial('-', 1)#1 means left, 2 means right
		while(sensor_collect[0] == -2):
			clear_comm()
			left.write(b"u")
			sensor_collect[0] = read_integer_serial('-', 1) 

		sensor_collect[1] = read_integer_serial('&', 1)
		while(sensor_collect[1] == -2):
			clear_comm()
			left.write(b"u")
			trash_value = read_integer_serial('-', 1)
			sensor_collect[1] = read_integer_serial('&',1)

		sensor_collect[2] = read_integer_serial('-', 2)
		while(sensor_collect[2] == -2):
			clear_comm()
			right.write(b"u")
			sensor_collect[2] = read_integer_serial('-', 2)

		sensor_collect[3] = read_integer_serial('&' , 2)
		while(sensor_collect[3] == -2):
			clear_comm()
			right.write(b"u")
			trash_value = read_integer_serial('-', 2)
			sensor_collect[3] = read_integer_serial('&' ,2)

		sensor_total[0] += sensor_collect[0]
		sensor_total[1] += sensor_collect[1]

		sensor_total[2] += sensor_collect[2]
		sensor_total[3] += sensor_collect[3] 
		

	left_back_ave = sensor_total[0] / sensor_collect_fre
	left_left_ave = sensor_total[1] / sensor_collect_fre

	right_front_ave = sensor_total[2] / sensor_collect_fre
	right_right_ave = sensor_total[3] / sensor_collect_fre


	print("LEFT: B:{B}	L:{L}	RIGHT: F:{F}	R:{R}".format(B = left_back_ave,L = left_left_ave,F = right_front_ave, R = right_right_ave) ) 
	print("\n")
	return
def capacitor_sensor():
	#The right arduino is the only arduino with a capacitive sensor
	sensor_data = [0,0,0] #Highest, median, and lowest
	clear_comm()

	print("Collecting data from Capacitive Sensor")

	for i in range(100):#This is the amount of attempts the Raspberry has to recieve the information
		clear_comm()
		right.write(b"C")
		sleep(0.5)
		sensor_data[0] = read_integer_serial('-', 2)
		print(sensor_data[0])
		sensor_data[1] = read_integer_serial('-', 2)
		print(sensor_data[1])
		sensor_data[2] = read_integer_serial('&', 2)
		print(sensor_data[2])

		if(sensor_data[0] != -2 and sensor_data[1] != -2 and sensor_data[2] != -2):
			print("Communication Success")
			print(sensor_data)
			break
	
		print("Communication Failure")
		print(sensor_data)

	
	return
def capacitor_hard_reset():
	right.write(b"H")
	print("Capacitor sensor reset")
	#This lets the capacitor reset 
	return
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
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )
	left.write(b"&")
	#Sending bytes to the right arduino
	right.write(bytes[0].encode() )
	right.write(bytes[1].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[2].encode() )
	right.write(b"&")
	return

def servo_info():
	left.write(b"n")
	right.write(b"n")
	
	left_servo_position = read_integer_serial('-' , 1)
	left_servo_height_top = read_integer_serial('-', 1)
	left_servo_height_bottom = read_integer_serial('&', 1)
	
	right_servo_position = read_integer_serial('-', 2)
	right_servo_height_top = read_integer_serial('-', 2)
	right_servo_height_bottom = read_integer_serial('&' , 2)
	
	print("Left Servo Information:")
	print("Position: {P} Height Top: {T} Height Bottom: {B}".format(P = left_servo_position, T = left_servo_height_top, B = left_servo_height_bottom) )
	print("Right Servo Information:")
	print("Position: {P} Height Top: {T} Height Bottom: {B}".format(P = right_servo_position, T = right_servo_height_top, B = right_servo_height_bottom) )
	
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
	
#This code is for the motor encoders

""" Time dependent calibration

def calibration_distance(axes):
	print("Calibration Iniciated")
	sleep(2)
	
	global cali_pres
	global time_distance_slope
	global time_distance_shift
	
	cali_pres = 1
	
	bytes = ['@','@', '@', '@', '@']
	bytes[1] = str( 250 )
	bytes[2] = str( 250 - 15 )
	bytes[3] = str( 250 )
	bytes[4] = str( 250 )
	print("250 to all motors")
	if(axes == 1):#Y Calibration
		move_forward(bytes)
	if(axes == 2):#X Calibration
		move_right(bytes)
	
	inital_time1 = time()
	print("Stopwatch start:")
	while(cali_pres == 1):
		sleep(0.001)
	print("Stopwatch stop!")
	stop()
	after_time1 = time()
	diff_time1 = after_time1 - inital_time1
	print("Time measured: {A}".format(A=diff_time1)) 
	
	print("Iniciating part 2")
	sleep(5)
	cali_pres = 1
	print("100 to all motors")
	bytes = ['@','@', '@', '@', '@']
	bytes[1] = str( 100 )
	bytes[2] = str( 100 - 15 )
	bytes[3] = str( 100 )
	bytes[4] = str( 100 )
	if(axes == 1):#Y Calibration
		move_forward(bytes)
	if(axes == 2):#X Calibration
		move_right(bytes)
	print("Stopwatch start:")
	inital_time2 = time()
	
	while(cali_pres == 1):
		sleep(0.001)
	print("Stopwatch stop!")
	stop()
	after_time2 = time()
	
	diff_time2 = after_time2 - inital_time2
	print("Time measured: {B}".format(B = diff_time2))
	if(axes == 1):#Y Calibration
		time_distance_slope['y'] = (diff_time1 - diff_time2)/(250-100)
		time_distance_shift['y'] = diff_time1-250*(time_distance_slope['y'])
		print("The slope is {A} and the shift is {B}".format(A=time_distance_slope['y'],B = time_distance_shift['y']) )
	if(axes == 2):#X Calibration	
		time_distance_slope['x'] = (diff_time1 - diff_time2)/(250-100)
		time_distance_shift['x'] = diff_time1-250*(time_distance_slope['x'])
		print("The slope is {A} and the shift is {B}".format(A=time_distance_slope['x'],B = time_distance_shift['x']) )
	
	return
"""
	
""" For time dependet system
def time_distance_function(speed,axes):
	if(axes == 1):#Y Calculation
		calculated_time = time_distance_slope['y']*speed + time_distance_shift['y']
	if(axes == 2):#X Calculation
		calculated_time = time_distance_slope['x']*speed + time_distance_shift['x']
	return calculated_time
	
"""

def encoder_calibration(axes,test_quantity):
	test_sample = [0,0,0,0]

	print("Calibration Iniciated")
	if axes == 1:
		print("Y axis selected")
	if axes == 2:
		print("X axis selected")
	print("Quantity of test: {A}".format(A = test_quantity))
	
	global cali_pres

	for i in range(test_quantity):

		encoder_reset()

		sleep(2)
		
		print("Beginning test {A}".format(A = i+1))

		cali_pres = 1
	
		bytes = ['@','@', '@', '@', '@']
		bytes[1] = str( 250 )
		bytes[2] = str( 250 )
		bytes[3] = str( 250 )
		bytes[4] = str( 250 )

		#print("250 to all motors")
	
		
		if(axes == 1):#Y Calibration
			for i in range(4):
				print("Motor speed changed to Y+ default")
				bytes[i + 1] = str(move_y_speed_p[i])
			move_forward(bytes)
		if(axes == 2):#X Calibration
			for i in range(4):
				print("Motor speed changed to X+ default")
				bytes[i + 1] = str(move_x_speed_p[i])
			move_right(bytes)

		while(cali_pres == 1):
			sleep(0.001)
		print("Stopwatch stop!")
		stop()
		encoder_update()
		for i in range(4):
			test_sample[i] = test_sample[i] + encoder_value[i]
	
	for i in range(4):
			test_sample[i] = test_sample[i] / test_quantity

	for i in range(4):#Transferring average to constant variable
		if axes == 1:#Y
			encoder_constant_y[i] = test_sample[i]
			print("{A}: {B}".format(A = i, B = encoder_constant_y[i]))
		if axes == 2:#X
			encoder_constant_x[i] = test_sample[i] 
			print("{A}: {B}".format(A = i, B = encoder_constant_x[i]))

	return


#Assigned the interrupt their functions
GPIO.add_event_detect(26, GPIO.RISING, callback = start_button_pressed, bouncetime = 300)


"""Gyro Code Ahead"""

""" 
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

"""

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

