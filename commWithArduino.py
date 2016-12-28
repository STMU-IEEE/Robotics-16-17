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

#inital commands to make sure the arduino is stop and communication is open

left.write(b"9")
right.write(b"9")

left.write(b"x")
right.write(b"x")

#functions that control the arduino

def end():
	"Stops the motors and disconnects the serial comm channels."##LINE 20
	stop()
	right.close()
	left.close()
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
	left.write(b"u")
	right.write(b"u")
	left_ultra = [0,0,0]
	left_amount = 0
	terminating_char = '-'
	#'-' separates values 
	#'&' ends of transmition
	while(True):
		if left_amount == 2:
			break

		new_character = left.read()

		if new_character == terminating_char:
			break

		new_integer = int(new_character)
		left_ultra[left_amount] = new_integer
		left_amount += 1

	for i in range(left_amount):
		number += left_ultra[i] * pow(10, i)
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
	print("Left: " + str(left.read() ) )
	print("Right: " + str(right.read() ) )
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
		

	return

#Here is the loop that recieves input from the user

print("Welcome to The Raspberry Pi Controller HQ")
print("When entering multiple bytes, the first bytes affect the left arduino and the motor A respectively")

while(True):
	x = input("Enter Command: ")
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)

GPIO.cleanup()




