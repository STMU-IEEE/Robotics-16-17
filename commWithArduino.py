from function import *
#from function import restart_comm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

FRONT_C = 1
LEFT_C = 2
RIGHT_C = 3
BACK_C = 4

#Switch Case that selects the commands
def command(x):

	bytes = x.split()

	#Motor Commands
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
	if bytes[0] == 'q':
		rotate_counter(bytes)
	if bytes[0] == 'e':
		rotate_clockwise(bytes)
	#Calibration and Distance Commands
	if bytes[0] == 'm':
		encoder_calibration(int(bytes[1]), int(bytes[2]))#Byte one(0 for Y and 1 for X), Byte Two(quantity of test)
	if bytes[0] == 'M':
		encoder_update()
	if bytes[0] == 'K':
		encoder_reset()
	if bytes[0] == 'B':
		encoder_update()
		encoder_current_value()
	if bytes[0] == 'H':
		encoder_constant_value()
	#regarding side, 0 is for positive direction, while 1 is for negative directions
	if bytes[0] == 'X':
		move_x(bytes[1], bytes[2])#side, speed
	if bytes[0] == 'Y':
		move_y(bytes[1], bytes[2])
	#Sensor Commands
	if bytes[0] == 'u':
		print(us_sensor())
	if bytes[0] == 'o':#reading the values of the capacitor sensor
		capacitor_sensor()
	if bytes[0] == '|':
		capacitor_report()
	if bytes[0] == 'h':
		capacitor_hard_reset()
	if bytes[0] == 'l':
		capacitor_calibration()
	if bytes[0] == 'v':
		print(capacitor_block_identity())#0 wire, 1 no wire no insulation, 2 insulation
	if bytes[0] == 'L':
		capacitor_calibrate_move(int(bytes[1]), int(bytes[2]), int(bytes[3]))
	if bytes[0] == 'V':
		capacitor_block_multiple(int(bytes[1])) #Quantity of test
	#Servo Command
	if bytes[0] == 't':
		servo_top(bytes[1])
	if bytes[0] == 'b':
		servo_bottom(bytes[1])
	if bytes[0] == 'n':
		servo_info()
	if bytes[0] == 'c':
		servo_change(bytes)
	if bytes[0] == 'p':
		servo_bottom(bytes[1])
		sleep(5)
		servo_top(bytes[1])
	#Communicatin Command
	if bytes[0] == 'R':
		restart_comm()
	if bytes[0] == 'C':
		clear_comm()
	"""
        Raspberry Pi Gyro Commands
	#Gyro Commands
	if bytes[0] == 'W':
		move_gyro(FRONT_C, bytes[1], bytes[2])
	if bytes[0] == 'A':
		move_gyro(LEFT_C, bytes[1], bytes[2])
	if bytes[0] == 'D':
		move_gyro(RIGHT_C, bytes[1], bytes[2])
	if bytes[0] == 'S':
		move_gyro(LEFT_C, bytes[1], bytes[2])
	if bytes[0] == 'Q':
		rotate_counter_gyro()
	if bytes[0] == 'E':
		rotate_clockwise_gyro()
	if bytes[0] == 'P':
		redefine_pre()
	if bytes[0] == 'F':
		redefine_fre(bytes[1])
	if bytes[0] == 'I':
		redefine_sensa(bytes[1])
	if bytes[0] == 'T':#testing
		redefine_pre()
		gyro_main()
	#Magnetometer Commands
	if bytes[0] == 'N':
		north()
	"""
	#Arduino Gyro Commands
	"""
	if bytes[0] == 'I':
		gyro_cali()
	if bytes[0] == 'A':
		gyro_update_angle()
	if bytes[0] == 'R':
		gyro_report_angle()
    """

	return

#Here is the loop that recieves input from the user

print("Welcome to The Raspberry Pi Controller HQ")
print("FRONT: 1, LEFT: 2, RIGHT: 3, BACK: 4")
print("Variable Speed: [direction (wasd) and x to stop] [Left A] [Left B] [Right A] [Right B]")
print("Move by axes and block: [direction (XY)] [positive or negative] [motor speed] [number of block] ")
print("Servo: FRONT = 1 BACK = 4 --> [up(t) or down(b) or pick_up(p)] [servo#]")
print("Gyro: [direction (caps motor's keys)] [max_speed] [gryo_sensativity]")
print("Communication Commands: [command (R or C)]")
print("Ultrasonic Sensor: 'u' ")
restart_comm()
clear_comm()
stop()
read_gyro_status()
assign_side()
#servo_top()
while(True):
	x = input("Enter Command: ")
	print(x)
	if x == '1':
		end()
		break
	else:
		command(x)

GPIO.cleanup()
