import RPi.GPIO as GPIO
import time
from display import *

seven_seg_setup()

while True:
	for i in range(0,16):
		seven_seg_turn_on(i)
		time.sleep(1)

