from sense_hat import SenseHat
import time
from math import log

sense = SenseHat()
timer = 0

#              (x, y, r, g, b)
sense.set_pixel(0, 0, 255, 255, 0)

for i in range(100):
	
	orientation = sense.get_orientation()
	orientation2 = orientation	
	time.sleep(1)
	timer = timer + 1
	orientation = sense.get_orientation()
	difference = orientation2['yaw'] - orientation['yaw'] - ((0.1481 * log(timer)) - 0.6134)
	print (difference)
