import serial
import Pathfinding
import sys
import time


"""This will be called at the beginning of the program to initialize everything."""

left_ard='/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400L3-if00'
right_ard='/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400T8-if00'
left = serial.Serial(left_ard, 9600)
right = serial.Serial(right_ard, 9600)

left.write(b"x")
right.write(b"x")

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
##LINE 30
def move_left():
	left.write(b"i")
	right.write(b"o")
	return

def move_right():
	right.write(b"i")
	left.write(b"o")
	return
##LINE 40

def move_forward():
	right.write(b"w")
	left.write(b"w")
	return

def move_reverse():
	left.write(b"r")
	right.write(b"r")
	return
##LINE 50
def us_sensor():
	left.write(b"u")
	right.write(b"u")
	##print("Left: " + left.read()  )
	##print("Right: " + right.read()  )
	return

def servo_top():
	left.write(b"t")
	right.write(b"t")
	return
##LINE 60
def servo_bottom():
	left.write(b"b")
	right.write(b"b")
	return


def command(x):

	if x == 'w':
		move_forward()
	if x == 'a':
		move_left()
	if x == 's':
		move_reverse()
	if x == 'd':
		move_right()
	if x == 'x':
		stop()
	if x == 'u':
		us_sensor()
	if x == 't':
		servo_top()
	if x == 'b':
		servo_bottom()

	return


print("Welcome to The Raspberry Pi Controller HQ")

while(True):
	x = input("Enter Command: ")
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)









