from sense_hat import SenseHat
import time
from math import log

sense = SenseHat()
timer = 1

#              (x, y, r, g, b)
sense.set_pixel(0, 0, 255, 255, 0) #Set LED at coordinate (0,0) to yellow. 

for i in range(100):
	
	raw_orientation = sense.get_orientation()
	adjusted_orientation = raw_orientation['yaw']  - 2.3975 * log(timer)
	print(adjusted_orientation)
	time.sleep(1) 
	timer = timer + 1

