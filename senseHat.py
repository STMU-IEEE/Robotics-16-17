from sense_hat import SenseHat
from time import *
from math import log
from random import randint

sense = SenseHat()
timer = 1

#              (x, y, r, g, b)
#sense.set_pixel(0, 0, 255, 255, 0) #Set LED at coordinate (0,0) to yellow. 
"""
for i in range(100):
	
	raw_orientation = sense.get_orientation()
	adjusted_orientation = raw_orientation['yaw']  - 2.3975 * log(timer)
	print(adjusted_orientation)
	time.sleep(1) 
	timer = timer + 1
"""
r = [255,0,0]
o = [255,127,0]
y = [255,255,0]
g = [0,255,0]
b = [0,0,255]
i = [75,0,130]
v = [159,0,255]
e = [0,0,0]

image = [
e,e,e,e,e,e,e,e,
e,e,e,r,r,e,e,e,
e,r,r,o,o,r,r,e,
r,o,o,y,y,o,o,r,
o,y,y,g,g,y,y,o,
y,g,g,b,b,g,g,y,
b,b,b,i,i,b,b,b,
b,i,i,v,v,i,i,b
]

sense.set_pixels(image)
