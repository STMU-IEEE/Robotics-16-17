import serial
import Pathfinding
import sys
import time
import RPi.GPIO as GPIO
import math
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
	return 
def stop():
	right.write(b"x")
	left.write(b"x")
	return

def move_right(bytes):
	left.write(b"i")
	left.write(bytes[1].encode() )
	left.write(b"&")#separator char
	left.write(bytes[2].encode() )

	right.write(b"o")
	right.write(bytes[3].encode() )
	right.write(b"&")#separator char
	right.write(bytes[4].encode() )
	return

def move_left(bytes):
	left.write(b"o")
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )

	right.write(b"i")
	right.write(bytes[3].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[4].encode() )
	return
##LINE 40

def move_forward(bytes):
	left.write(bytes[0].encode() )
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )

	right.write(bytes[0].encode() )
	right.write(bytes[3].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[4].encode() )
	return

def move_reverse(bytes):
	left.write(b"r")
	left.write(bytes[1].encode() )
	left.write(b"&")#Separator Char
	left.write(bytes[2].encode() )

	right.write(b"r")
	right.write(bytes[3].encode() )
	right.write(b"&")#Separator Char
	right.write(bytes[4].encode() )
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
""" 
def read_integer_serial(terminating_char, side):
	#side if 1 means left and 2 means right
	#'-' separates values 
	#'&' ends of transmition
	char_read = [-1,-1,-1]
	if side == 1:#left
		#print("left")
		for i in range(3):#Read the char and end if read char is the terminating_char
			new_char = left.read()
			if len(new_char) == 0:
				print("Left Ultrasonic Failure")
				return -2
			new_char = ord(new_char) - 48 #- will return -3
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
		else:
			return int(char_read[0]) * 100  + int( char_read[1] ) * 10  + int( char_read[2] )
	if side == 2:#right
		#print("right")
		for i in range(3):#Read the char and end if read char is the terminating_char
			new_char = right.read()
			if len(new_char) == 0:
				print("Right Ultrasonic Failure")
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
		else:
			return int(char_read[0]) * 100  + int( char_read[1] ) * 10 + int( char_read[2] )
		
"""
#Assigned the interrupt their functions
GPIO.add_event_detect(26, GPIO.RISING, callback = start_button_pressed, bouncetime = 300)

#Switch Case that selects the commands
def command(x):

	bytes = x.split()

	if bytes[0] == 'w':
		move_forward(bytes)
	if bytes[0] == 'a':
		move_left(bytes)
	if bytes[0] == 's':
		move_reverse(bytes)
	if bytes[0] == 'd':
		move_right(bytes)
	if bytes[0] == 'x':
		stop()
	if bytes[0] == 'u':
		us_sensor()
	if bytes[0] == 't':
		servo_top()
	if bytes[0] == 'b':
		servo_bottom()
	if bytes[0] == 'n':
		servo_info()
	if bytes[0] == 'c':
		servo_change(bytes)
	if bytes[0] == '9':
		restart_comm()
	if bytes[0] == '0':
		clear_comm()
	if bytes[0] == 'p':
		servo_bottom()
		sleep(5)
		servo_top()
	#This is are commands with gyro 
	if bytes[0] == 'W':
		print("Still in progress")				
	return

#Here is the loop that recieves input from the user

print("Welcome to The Raspberry Pi Controller HQ")
print("When entering multiple bytes, the first bytes affect the left arduino and the motor A respectively")
restart_comm()
clear_comm()
stop()
servo_top()
while(True):  
	x = input("Enter Command: ")
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)
	
GPIO.cleanup()




