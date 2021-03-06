import serial
#import gyro 
from time import sleep

""" 
This is the id of the black arduino Uno

'/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'


This is the id of the athuentic arduino uno
'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'

This is the id of one of the arduino 101s
'/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400T8-if00'

"""




left_ard = '/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'
right_ard  = '/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'


right = serial.Serial(right_ard, 9600)
left = serial.Serial(left_ard, 9600)

def stop_motor():
	left.write(b"x")
	right.write(b"x")

def end():
	stop_motor()
	left.close()
	right.close()
	return



""" Previous Code
def light_on():
	ard.write(b"1")
	return

def light_off():
	ard.write(b"0")
	return

def read_state():
	ard.write(b"p")
	info = ard.read()
	if info == b'0':
		print("The LED is OFF")
	else:
		print("The LED is ON")
	return
"""

def command(x):

	""" Previous Code
	if x == '1':
		light_on()
	if x == '0':
		light_off()
	if x == 'p':
		read_state()
	"""

	if x == 'u':
		left.write(b"u")
		right.write(b"u")
		ultrasonic_left = left.read()
		ultrasonic_right = right.read()
		print("Left Arduino Info: " + ultrasonic_left)
		print("Right Arduino Info: " + ultrasonic_right)
	bytes = x.split()

	if bytes[0] == 'w':
		print(""" Moving_Forwards: ARD_R: A- {am1_speed} B- {bm1_speed},ARD_L: A- {am2_speed} B-{bm2_speed}""".format(am1_speed = bytes[1],
			 bm1_speed = bytes[2], am2_speed = bytes[3], bm2_speed = bytes[4]))

		left.write( bytes[0].encode() )

		left.write( bytes[1].encode() )
		left.write( b"&")
		#sleep(1.1)
		left.write( bytes[2].encode() )

		right.write( bytes[0].encode() )

		right.write( bytes[3].encode() )
		right.write( b"&")
		#sleep(1.1)
		right.write( bytes[4].encode() )
		
	if bytes[0] == 's':
		print("Moving_Backwards")
	if x == 'x':
		stop_motor()
	if x == '9':
		left.write(b"9")
		right.write(b"9")		
	return


print("Welcome to The Raspberry Pi Controller HQ")
print("Enter direction, ARD1 AMOTOR speed,ARD1 BMOTOR speed,ARD2 AMOTOR speed,ARD2 BMOTORspeed")
while(True):
	x = input("Enter Command: ")
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)


