from sense_hat import SenseHat
import time

sense = SenseHat()
orientation = sense.get_orientation()

while True:
 	
	orientation2 = sense.get_orientation()
	
	if abs(orientation2['yaw'] - orientation['yaw']) >= 1:
		orientation = orientation2
	
	time.sleep(1)
	print(orientation['yaw'])
