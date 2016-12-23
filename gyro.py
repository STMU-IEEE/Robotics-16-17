from sense_hat import SenseHat
from time import sleep
import serial 
"""  
left_ard = '/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00'
right_ard = '/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00'

left = serial.Serial(left_ard, 9600)
right = serial.Serial(right_ard, 9600)

left.write(b"9")
right.write(b"9")
"""
sense = SenseHat()

FRO_LEFT = "fro_left"
FRO_RIGHT = "fro_right"
BAC_LEFT = "bac_left"
BAC_RIGHT = "bac_right"


#for testing purposes
#for i in range(400):
	#new_value = sense.get_orientation()
	#diff = inital_value["yaw"] - new_value["yaw"]
	#print(diff )
	#print( new_value["yaw"] )
	#sleep(0.01)

def ave_gyro():

	fre = 25
	inital_value  = sense.get_orientation()
	total =  inital_value["yaw"]

	for i in range(fre):
	
		new_value = sense.get_orientation()
		total = total + new_value["yaw"]
		sleep(0.01)

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
#inital conditions
direction = 1
motor_speed = {'fro_left': 255, 'fro_right': 255, 'bac_left': 255, 'bac_right': 255}


def change_speed(x):
	if direction == 1:#Moving Forward
		""" 
		if abs(x) < 1:#Robot is going straight
			motor_speed[FRO_LEFT] = 225
			motor_speed[FRO_RIGHT] = 255
			motor_speed[BAC_LEFT] = 255
			motor_speed[BAC_RIGHT] = 255
		"""
		if x < -1:#counter-clockwise rotation, decrease right and increase left
			print("Counter-ClockWise with difference of {diff}".format(diff = str(x)))
			value_i = 0
			flag = 0
			""" 
			for i in range(10):
				if motor_speed[FRO_LEFT] + abs(x)*((10 - i)/10) < 250 and motor_speed[BAC_LEFT] + abs(x) *((10 - i )/10) < 250:
					value_i = i
					flag = 1
					print("hello")
					break
			if flag == 0:
				motor_speed[FRO_LEFT] += abs(x) * (10 - value_i) / 10
				motor_speed[BAC_LEFT] += abs(x) * (10 - value_i) / 10
				motor_speed[FRO_RIGHT] -= abs(x) * value_i / 10
				motor_speed[BAC_RIGHT] -= abs(x) * value_i / 10
			else:
				motor_speed[FRO_RIGHT] -= abs(x)
				motor_speed[BAC_RIGHT] -= abs(x)
			"""
			if motor_speed[FRO_LEFT] + abs(x) < 250 and motor_speed[BAC_LEFT] + abs(x) < 250:
				motor_speed[FRO_LEFT] += abs(x)
				motor_speed[BAC_LEFT] += abs(x)
			else:
				motor_speed[FRO_RIGHT] -= abs(x)
				motor_speed[BAC_RIGHT] -= abs(x)

		if x > 1:#clockwise rotation, decrease left and increase right
			print("ClockWise with difference 0f {diff}".format(diff = str(x) ) )
			value_j = 0
			""" 
			for j in range(10):
				if motor_speed[FRO_RIGHT] + abs(x) * (10 - j)/10 < 255 and motor_speed[BAC_RIGHT] + abs(x) * (10- j)/10 < 255:
					value_j = j
					break
			motor_speed[FRO_RIGHT] += abs(x) * (10 - value_j) / 10
			motor_speed[BAC_RIGHT] += abs(x) * (10 - value_j) / 10

			motor_speed[FRO_LEFT] -= abs(x) * value_j / 10
			motor_speed[BAC_LEFT] -= abs(x) * value_j / 10
			"""
			if motor_speed[FRO_RIGHT] + abs(x) < 250 and motor_speed[BAC_LEFT] + abs(x) < 250:
				motor_speed[FRO_RIGHT] += abs(x)
				motor_speed[BAC_RIGHT] += abs(x)
			else:
				motor_speed[FRO_LEFT] -= abs(x)
				motor_speed[BAC_LEFT] -= abs(x)

	if direction == 2:#Moving Leftward
		print("Going Leftward")
	if direction == 3:#Moving Rightward
		print("Going Rightward")
	if direction == 4:#Moving Backward
		print("Going Backward")

	#sending new speeds to the arduinos
	print(' {f_L}  {f_R} '.format(f_L = str(motor_speed[FRO_LEFT]), f_R = str(motor_speed[FRO_RIGHT])  ) )
	print(' {b_L}  {b_R} '.format(b_L = str(motor_speed[BAC_LEFT]), b_R = str(motor_speed[BAC_RIGHT])  ) ) 
	print('\n')
	""" 
	left.write(b"w")
	left.write( str ( motor_speed[FRO_LEFT] ).encode() )
	left.write(b"A")
	left.write( str ( motor_speed[BAC_LEFT] ).encode() )

	right.write(b"w")
	right.write( str ( motor_speed[FRO_RIGHT] ).encode() )
	right.write(b"A")
	right.write( str ( motor_speed[BAC_RIGHT] ).encode() )
	""" 
	return

def displacement():
	B = ave_gyro()
	print(pre_value - B)	
def rotation():
	A = ave_gyro()
	B = ave_gyro()
	if B - A > 0.6:
		print("ClockWise: {diff}".format(diff = (B-A) ) )
	if B - A < -0.6:
		print("CounterClockWise: {diff}".format(diff = (B-A) ) )
	if abs( B - A ) <  0.6 :
		print("Stationary")

def move_straight(direction):
	#Code to make the robot move straight
	post_value = ave_gyro()
	diff = post_value - pre_value
	change_speed(diff)	

def main():
	while(True):
		#move_straight(1)
		#print(ave_gyro() )
		#rotation()
		displacement() 

pre_value = ave_gyro()
main()
