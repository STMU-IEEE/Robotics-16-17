from sense_hat import SenseHat
from time import sleep
import serial
import colorama 
from colorama import Fore, Back, Style
#"""
    
left_ard = '/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'
right_ard = '/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'

left = serial.Serial(left_ard, 9600)
right = serial.Serial(right_ard, 9600)

left.write(b"9")
right.write(b"9")
#"""

sense = SenseHat()

FRO_LEFT = "fro_left"
FRO_RIGHT = "fro_right"
BAC_LEFT = "bac_left"
BAC_RIGHT = "bac_right"

direction = 1
motor_speed = {'fro_left': 255, 'fro_right': 255, 'bac_left': 255, 'bac_right': 255}

def get_gyro_reading():

	motion = sense.get_orientation()
	return motion["yaw"]

def ave_gyro():

	fre = 75
	inital_value  = sense.get_orientation()
	total =  inital_value["yaw"]

	for i in range(fre):
		new_value = get_gyro_reading()
		total +=  new_value

	ave = total / fre
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
	RIGHT_CHANGE  = 0
	LEFT_CHANGE = 0#1 means green and 2 means red and 0 means no change
	largest_value = 0
	factor = 3

	if abs(x) < 1:#Robot is going straight
		if motor_speed[FRO_LEFT] > largest_value:
			largest_value = motor_speed[FRO_LEFT]
		if motor_speed[BAC_LEFT] > largest_value:
			largest_value = motor_speed[BAC_LEFT]
		if motor_speed[FRO_RIGHT] > largest_value:
			largest_value = motor_speed[FRO_RIGHT]
		if motor_speed[BAC_RIGHT] > largest_value:
			largest_value = motor_speed[BAC_RIGHT]

		motor_speed[FRO_LEFT] = largest_value + 5
		motor_speed[FRO_RIGHT] = largest_value + 5
		motor_speed[BAC_LEFT] = largest_value + 5
		motor_speed[BAC_RIGHT] = largest_value + 5

	if direction == 1:#Moving Forward
		print("Going Forward")		 
		if x < -1:#counter-clockwise rotation, decrease right and increase left
			print("Counter-ClockWise with difference of {diff}".format(diff = str(x)))

			if motor_speed[FRO_LEFT] + abs(x) < 250 and motor_speed[BAC_LEFT] + abs(x) < 250:
				motor_speed[FRO_LEFT] += abs(x) * factor
				motor_speed[BAC_LEFT] += abs(x) * factor
				LEFT_CHANGE = 1
				#print("LEFT_CHANGE is 1")
			else:
				motor_speed[FRO_RIGHT] -= abs(x) * factor
				motor_speed[BAC_RIGHT] -= abs(x) * factor
				RIGHT_CHANGE = 2
				#print("RIGHT_CHANGE is 2")

		if x > 1:#clockwise rotation, decrease left and increase right
			print("ClockWise with difference 0f {diff}".format(diff = str(x) ) )

			if motor_speed[FRO_RIGHT] + abs(x) < 250 and motor_speed[BAC_LEFT] + abs(x) < 250:
				motor_speed[FRO_RIGHT] += abs(x) * factor
				motor_speed[BAC_RIGHT] += abs(x) * factor
				RIGHT_CHANGE = 1
				#print("RIGHT_CHANGE is 1")
			else:
				motor_speed[FRO_LEFT] -= abs(x) * factor
				motor_speed[BAC_LEFT] -= abs(x) * factor
				LEFT_CHANGE = 2
				#print("LEFT_CHANGE is 2")
				
	if direction == 2:#Moving Leftward
		print("Going Leftward")
	if direction == 3:#Moving Rightward
		print("Going Rightward")
	if direction == 4:#Moving Backward
		print("Going Backward")
	
	speed_constraint()
	speed_display(LEFT_CHANGE, RIGHT_CHANGE)
	send_speed()

	return 

def speed_constraint():
	lowest_speed = 0
	max_speed = 250
	#speed Restrictions
	if motor_speed[FRO_LEFT] > max_speed:
		motor_speed[FRO_LEFT] = max_speed
	if motor_speed[FRO_LEFT] < lowest_speed:
		motor_speed[FRO_LEFT] = lowest_speed

	if motor_speed[FRO_RIGHT] > max_speed:
		motor_speed[FRO_RIGHT] = max_speed
	if motor_speed[FRO_RIGHT] < lowest_speed:
		motor_speed[FRO_RIGHT] = lowest_speed

	if motor_speed[BAC_LEFT] > max_speed:
		motor_speed[BAC_LEFT] = max_speed
	if motor_speed[BAC_LEFT] < lowest_speed:
		motor_speed[BAC_LEFT] = lowest_speed

	if motor_speed[BAC_RIGHT] > max_speed:
		motor_speed[BAC_RIGHT] = max_speed
	if motor_speed[BAC_RIGHT] < lowest_speed:
		motor_speed[BAC_RIGHT] = lowest_speed
	return

def speed_display(LEFT_CHANGE, RIGHT_CHANGE):
	#1 means green, 2 means red and 0 means white
	#printing the speeds with the corresponding color 
	print("LEFT: {L} RIGHT: {R}".format(L = LEFT_CHANGE, R = RIGHT_CHANGE) )
	
	if LEFT_CHANGE == 1 and RIGHT_CHANGE == 2:#green and red 
		print(Fore.GREEN + ' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) + Fore.RED +     ' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Fore.GREEN + ' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) + Fore.RED +    ' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) ) 
	
	if LEFT_CHANGE == 2 and RIGHT_CHANGE == 1:#red and green
		print(Fore.RED +   ' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) +  Fore.GREEN  + ' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Fore.RED +   ' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) +  Fore.GREEN  + ' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) )

	if LEFT_CHANGE == 0 and RIGHT_CHANGE == 1:#nothing and green
		print(Style.RESET_ALL +' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) +Fore.GREEN+ ' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Style.RESET_ALL +' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) +Fore.GREEN+ ' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) )

	if LEFT_CHANGE == 1 and RIGHT_CHANGE == 0:#green and nothing
		print(Fore.GREEN + ' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) +Style.RESET_ALL+' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Fore.GREEN + ' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) +Style.RESET_ALL+' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) )

	if LEFT_CHANGE == 2 and RIGHT_CHANGE == 0:#red and nothing
		print(Fore.RED +   ' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) +Style.RESET_ALL+' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Fore.RED +   ' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) +Style.RESET_ALL+' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) )

	if LEFT_CHANGE == 0 and RIGHT_CHANGE == 2:#nothing and red
		print(Style.RESET_ALL +' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) + Fore.RED + ' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Style.RESET_ALL +' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) + Fore.RED + ' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) )

	if LEFT_CHANGE == 0 and RIGHT_CHANGE == 0:#nothing and nothing
		print(Style.RESET_ALL +' {f_L} '.format(f_L = str(motor_speed[FRO_LEFT])) + Style.RESET_ALL + ' {f_R} '.format( f_R = str(motor_speed[FRO_RIGHT])  ) )
		print(Style.RESET_ALL +' {b_L} '.format(b_L = str(motor_speed[BAC_LEFT])) + Style.RESET_ALL + ' {b_R} '.format( b_R = str(motor_speed[BAC_RIGHT])  ) )
	print(Style.RESET_ALL + "\n")
	return


def send_speed():
	print("{A}, {B}, {C}, {D}".format(A = motor_speed[FRO_LEFT], B = motor_speed[BAC_LEFT], C = motor_speed[FRO_RIGHT], D = motor_speed[BAC_RIGHT]  ) ) 
  
	left.write(b"w")
	left.write( str ( motor_speed[FRO_LEFT] ).encode() )
	left.write(b"&")
	left.write( str ( motor_speed[BAC_LEFT] ).encode() )

	right.write(b"w")
	right.write( str ( motor_speed[FRO_RIGHT] ).encode() )
	right.write(b"&")
	right.write( str ( motor_speed[BAC_RIGHT] ).encode() )
	"""  
	left.write(b"w")
	left.write(b"0")
	left.write(b"&")
	left.write(b"0")

	right.write(b"w")
	right.write(b"100")
	right.write(b"&")
	right.write(b"100")
	""" 
	return

def displacement():
	B = ave_gyro()
	diff = (pre_value - B) 
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

def move_stra(direction):
	#Code to make the robot move straigh
	pre_value = ave_gyro()
	change_speed( displacement() )

def gyro_main():
	while(True):
		move_stra(1)
		#print( ave_gyro() )
		#print(get_gyro_reading() )
		#rotation()
		#print( displacement() )
pre_value = ave_gyro()		
gyro_main()
