﻿import serial
import Pathfinding
import sys

options = {}
left = right = 0

def init():
    "This will be called at the beginning of the program to initialize everything."
    left_ard='/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400L3-if00'
    right_ard='/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400T8-if00'
    left = serial.Serial(left_ard, 9600)
    right = serial.Serial(right_ard, 9600)
    left.write(b"x")
    right.write(b"x")


        # map the inputs to the function blocks
    options = {"w" : move_forward,
           "a" : move_left,
           "s" : stop,
           "d" : move_right,
           "x" : end,
           "u" : us_sensor,
           "t" : servo_top,
           "b" : servo_bottom
           }
    print options
    return



def end():
    "Stops the motors and disconnects the serial comm channels."
    stop()
    right.close()
    left.close()
    return

def stop():
    right.write(b"x")
    left.write(b"x")
    return

def move_left():
    left.write(b"i")
    right.write(b"o")
    return

def move_right():
    right.write(b"i")
    left.write(b"o")
    return

def move_forward():
    right.write(b"f")
    left.write(b"f")
    return

def move_reverse():
    left.write(b"r")
    right.write(b"r")
    return

def us_sensor():
    left.write(b"u")
    right.write(b"u")
    return

def loop():
    x = raw_input("Enter Command: ")
    print x
    options[str(x)]
    return

def servo_top():
    left.write(b"t")
    right.write(b"t")
    return

def servo_bottom():
    left.write(b"b")
    right.write(b"b")
    return


	
init()

print("Welcome to The Raspberry Pi Controller HQ")

while(True):

    loop()

end()








