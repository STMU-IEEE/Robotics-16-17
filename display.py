#This is where the 7 segment code will be created
#also all of the code for the 8x8 matrix

"""
Purpose of Pin	7Seg Pin --- RPi Pin ---
	B				2			40
	A				3			33
	Latch				5			31
	D				12			29
	C				13			35
 Blanking 				8			38
"""

import RPi.GPIO as GPIO

def seven_seg_setup():
	if GPIO.getmode() is None:
		GPIO.cleanup
		GPIO.setmode(GPIO.BOARD)
	GPIO.setup(40, GPIO.OUT)
	GPIO.setup(33, GPIO.OUT)
	GPIO.setup(31, GPIO.OUT)
	GPIO.setup(29, GPIO.OUT)
	GPIO.setup(35, GPIO.OUT)
	GPIO.setup(38, GPIO.OUT)

	GPIO.output(40, GPIO.LOW)
	GPIO.output(33, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(35, GPIO.LOW)

	GPIO.output(38, GPIO.HIGH)

def seven_seg_turn_off():
	GPIO.output(38, GPIO.HIGH)
	return

def seven_seg_reset():
	GPIO.output(40, GPIO.LOW)
	GPIO.output(33, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(35, GPIO.LOW)

def seven_seg_turn_on(num):
	GPIO.output(38,GPIO.LOW)
	print(num)
	print()
	one = int(num) % 2
	two = (int(num)/2) % 2
	four = (int(num)/4) % 2
	eight = (int(num)/8) % 2

	if(int(one) == 1):
		GPIO.output(33,GPIO.HIGH)
		print('1')
	else:
		GPIO.output(33,GPIO.LOW)
		print('0')

	if(int(two) == 1):
		GPIO.output(40,GPIO.HIGH)
		print('1')
	else:
		GPIO.output(40,GPIO.LOW)
		print('0')

	if(int(four) == 1):
		GPIO.output(35,GPIO.HIGH)
		print('1')
	else:
		GPIO.output(35, GPIO.LOW)
		print('0')

	if(int(eight) == 1):
		GPIO.output(29,GPIO.HIGH)
		print('1')
	else:
		GPIO.output(29,GPIO.LOW)
		print('0')
	print()
	return
