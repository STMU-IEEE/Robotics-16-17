import serial


"""This will be called at the beginning of the program to initialize everything.
"""

"""
This is the id of the black arduino Uno

'/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'


This is the id of the athuentic arduino uno
'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'

This is the id of one of the arduino 101s
'/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400T8-if00'


"""

ardCom = '/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'



ard = serial.Serial(ardCom, 9600)


def end():
	ard.close()
	return

def light_on():
	ard.write(b"1")
	return

def light_off():
	ard.write(b"0")
	return

def read_state():
	ard.write(b"s")
	info = ard.read()
	if info == b'0':
		print("The LED is OFF")
	else:
		print("The LED is ON")
	return

def command(x):

	if x == '1':
		light_on()
	if x == '0':
		light_off()
	if x == 's':
		read_state()
	return


print("Welcome to The Raspberry Pi Controller HQ")

while(True):
	x = input("Enter Command: ")
	print(x)
	if x == 'x':
		end()
		break
	else:
		command(x)


