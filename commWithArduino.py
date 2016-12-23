import serial
import Pathfinding
import sys
import time
import RPi.GPIO as GPIO
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

def move_right():
	left.write(b"i")
	right.write(b"o")
	return

def move_left():
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

def servo_bottom():
	left.write(b"b")
	right.write(b"b")
	return
def restart_comm():
	left.write(b"9")
	right.write(b"9")
	return

#Function that occurs when stop and/or start button are pressed

def start_button_pressed(channel):
	#This is where the program to solve the "maze" would go
	#for now it just makes the robot move foward
	move_forward()
	return

#Assigned the interrupt their functions
GPIO.add_event_detect(26, GPIO.RISING, callback = start_button_pressed, bouncetime = 300)

#Switch Case that selects the commands
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
	if x == '9':
		restart_comm()
		

	return

#Here is the loop that recieves input from the user

print("Welcome to The Raspberry Pi Controller HQ")

while(True):
	x = input("Enter Command: ")
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)

GPIO.cleanup()




