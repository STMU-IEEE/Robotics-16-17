import serial
import Pathfinding
import sys
import RPi.GPIO as GPIO
import math 
from sense_hat import SenseHat
from time import sleep
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

#functions that control the arduino

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
	left.write(b"i")
	left.write(bytes[1].encode() )
	left.write(b"-")#separator char
	left.write(bytes[2].encode() )
	left.write(b"&")

	right.write(b"o")
	right.write(bytes[3].encode() )
	right.write(b"-")#separator char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return

def move_left(bytes):
	left.write(b"o")
	left.write(bytes[1].encode() )
	left.write(b"-")#Separator Char
	left.write(bytes[2].encode() )
	left.write(b"&")

	right.write(b"i")
	right.write(bytes[3].encode() )
	right.write(b"-")#Separator Char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return
##LINE 40

def move_forward(bytes):
	left.write(b"w")
	left.write(bytes[1].encode() )
	left.write(b"-")#Separator Char
	left.write(bytes[2].encode() )
	right.write(b"&")

	right.write(b"w")
	right.write(bytes[3].encode() )
	right.write(b"-")#Separator Char
	right.write(bytes[4].encode() )
	right.write(b"&")
	return

def move_reverse(bytes):
	left.write(b"r")
	left.write(bytes[1].encode() )
	left.write(b"-")#Separator Char
	left.write(bytes[2].encode() )
	left.write(b"&")

	right.write(b"r")
	right.write(bytes[3].encode() )
	right.write(b"-")#Separator Char
	right.write(bytes[4].encode() )
	right.write(b"&")
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
	""" 
	print("		    FRONT   ")
	print("	             {f}    ".format(f = right_front) )
	print("		[]--------[]")
	print("		|          |")
	print("		|          |")
	print("    {L}		|          |      {R}".format(L = left_left, R = right_right) )
	print("		|          |")
	print("		|          |")
	print("		[]--------[]")
	print("		     {b}    ".format(b = left_back) )
	print("	            BACK    ")
	"""
	print("LEFT: B:{B}	L:{L}	RIGHT: F:{F}	R:{R}".format(B = left_back_ave,L = left_left_ave,F = right_front_ave, R = right_right_ave) ) 
	print("\n")
	return

def servo_top():
	left.write(b"t")
	right.write(b"t")
	return

def servo_bottom():
	left.write(b"b")
	right.write(b"b")
	return

def servo_change(bytes):
	bytes[1] = servoH_top
	bytes[2] = servoH_bottom
	#Sending bytes to the left arduino
	left.write(bytes[0].encode() )
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )
	#Sending bytes to the right arduino
	right.write(bytes[0].encode() )
	right.write(bytes[1].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[2].encode() )
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
	left.write(b"9")
	right.write(b"9")
	return

#Function that occurs when stop and/or start button are pressed

def start_button_pressed(channel):
	#This is where the program to solve the "maze" would go
	#for now it just makes the robot move foward
	restart_comm()
	return
	
#Assigned the interrupt their functions
GPIO.add_event_detect(26, GPIO.RISING, callback = start_button_pressed, bouncetime = 300)


""" Gyro Code Ahead """

#Setting up gyro sensitive variables
sense = SenseHat()

FRONT_LEFT = "front_left"
FRONT_RIGHT = "front_right"
BACK_LEFT = "back_left"
BACK_RIGHT = "back_right"

FRONT = 1
LEFT = 2
RIGHT = 3
BACK = 4

pre_value = 0
direction = 0
motor_speed = {'front_left': 255, 'front_right': 255, 'back_left': 255, 'back_right': 255}
motor_change = [0,0,0,0]

def get_gyro_reading():

	motion = sense.get_orientation()
	return motion["yaw"]

def ave_gyro():

	fre = 300
	inital_value  = get_gyro_reading()
	total =  inital_value

	for i in range(fre):
		new_value = get_gyro_reading()
		total +=  new_value

	ave = total / (fre + 1)
	return ave
	

"""Information Here
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

#creates the new motor speeds to correct leaning
def change_speed(x):
	#This is to marrk which side the robot is leaning and what color must the text be printed to resemble increase and decrease
	largest_value = 0
	factor = 5
	global motor_speed
	 
	if abs(x) < 1:#Robot is going straight
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
	

	if direction == FRONT:#Moving Forward
		print("Going Forward")		 
		if x < -1:#counter-clockwise rotation, decrease right and increase left
			print("Counter-ClockWise with difference of {diff}".format(diff = str(x)))

			if motor_speed[FRONT_LEFT] + abs(x) < 250 and motor_speed[BACK_LEFT] + abs(x) < 250:
				motor_speed[FRONT_LEFT] += abs(x) * factor
				motor_speed[BACK_LEFT] += abs(x) * factor
				
				motor_change[0] = 1
				motor_change[1] = 1
				motor_change[2] = 0
				motor_change[3] = 0
				#print("LEFT_CHANGE is 1")
			else:
				motor_speed[FRONT_RIGHT] -= abs(x) * factor
				motor_speed[BACK_RIGHT] -= abs(x) * factor
				
				motor_change[2] = 2
				motor_change[3] = 2
				motor_change[0] = 0
				motor_change[1] = 0
				#print("RIGHT_CHANGE is 2")

		if x > 1:#clockwise rotation, decrease left and increase right
			print("ClockWise with difference 0f {diff}".format(diff = str(x) ) )

			if motor_speed[FRONT_RIGHT] + abs(x) < 250 and motor_speed[BACK_LEFT] + abs(x) < 250:
				motor_speed[FRONT_RIGHT] += abs(x) * factor
				motor_speed[BACK_RIGHT] += abs(x) * factor
				
				motor_change[2] = 1
				motor_change[3] = 1
				motor_change[0] = 0
				motor_change[1] = 0
				#print("RIGHT_CHANGE is 1")
			else:
				motor_speed[FRONT_LEFT] -= abs(x) * factor
				motor_speed[BACK_LEFT] -= abs(x) * factor
				
				motor_change[0] = 2
				motor_change[1] = 2
				motor_change[2] = 0
				motor_change[3] = 0
				#print("LEFT_CHANGE is 2")
				
	if direction == LEFT:#Moving Leftward
		print("Going Leftward")
	if direction == RIGHT:#Moving Rightward
		print("Going Rightward")
	if direction == BACK:#Moving Backward
		print("Going Backward")

	return 

def speed_constraint():
	lowest_speed = 0
	max_speed = 250
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

	if motor_speed[BACK_LEFT] > max_speed:
		motor_speed[BACK_LEFT] = max_speed
	if motor_speed[BACK_LEFT] < lowest_speed:
		motor_speed[BACK_LEFT] = lowest_speed

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
		
	
	if motor_change[2] == 1: #green
		print(Fore.GREEN + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )
	if motor_change[2] == 2: #red	
		print(Fore.RED + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )
	if motor_change[2] == 0: #white
		print(Style.RESET_ALL + ' {f_R} '.format(f_R = str(motor_speed[FRONT_RIGHT])), end = "" )
	
	print("\n")
	
	if motor_change[1] == 1: #green
		print(Fore.GREEN + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )
	if motor_change[1] == 2: #red	
		print(Fore.RED + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )
	if motor_change[1] == 0: #white
		print(Style.RESET_ALL + ' {b_L} '.format(b_L = str(motor_speed[BACK_LEFT])), end = "" )
		
	if motor_change[3] == 1: #green
		print(Fore.GREEN + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )
	if motor_change[3] == 2: #red	
		print(Fore.RED + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )
	if motor_change[3] == 0: #white
		print(Style.RESET_ALL + ' {b_R} '.format(b_R = str(motor_speed[BACK_RIGHT])), end = "" )
		
	print(Style.RESET_ALL + "\n")
	return


def send_speed():
	bytes = ['@','@', '@', '@', '@']
	fix_bias = 0#15
	print("L- A:{AL} B:{BL} R- A:{AR} B:{BR}".format(AL = motor_speed[FRONT_LEFT], BL = motor_speed[BACK_LEFT], AR = motor_speed[FRONT_RIGHT], BR = motor_speed[BACK_RIGHT] ) )
	bytes[1] = str( motor_speed[FRONT_LEFT] )
	bytes[2] = str( motor_speed[BACK_LEFT] - fix_bias )
	bytes[3] = str( motor_speed[FRONT_RIGHT] )
	bytes[4] = str( motor_speed[BACK_RIGHT] )

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

def displacement():
	#global pre_value
	new_value_gyro = ave_gyro()
	#print("pre_value: {P}".format( P = pre_value) )
	#print("new value: {B}".format( B = new_value_gyro) )
	diff = (pre_value - new_value_gyro) 
	return diff

def rotation():
	A = ave_gyro()
	B = ave_gyro()
	if B - A > 0.6:
		print("ClockWise: {diff}".format(diff = (B-A) ) )
	if B - A < -0.6:
		print("CounterClockWise: {diff}".format(diff = (B-A) ) )
	if abs( B - A ) <  0.6 :
		print("Stationary")

def move_gyro(direct):
	#Code to make the robot move straigh
	global direction
	direction = direct#making a local variable a global variable
	redefine_pre()
	while(True):
		change_speed( displacement() )
		speed_constraint()
		speed_display()
		send_speed()
	return
	
def gyro_main():
	while(True):
		#move_gyro(FRONT)
		#print( ave_gyro() )
		#print(get_gyro_reading() )
		#rotation()
		#print( displacement() )
		bytes = ['@', '@', '@', '@', '@' ]
		for i in range(20):
			bytes[1] = str(250 - i * 10)
			bytes[2] = bytes[1]
			bytes[3] = bytes[1] 
			bytes[4] = bytes[1]
			sleep(2)
			print(250 - i * 10) 
			move_forward(bytes)
		return 

def redefine_pre():
	global pre_value
	pre_value  = ave_gyro()
	print("Now the value of Pre is {Pre}".format(Pre = pre_value) )
	return
""" 
def ratio_function(diff):
	if diff == 10:
"""		
