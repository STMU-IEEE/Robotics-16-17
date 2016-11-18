import serial
import Pathfinding

init()
while(true)
    loop()

end()







def init():
    "This will be called at the beginning of the program to initialize everything."
    left_ard='/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400L3-if00'
    right_ard='/dev/serial/by-id/usb-Intel_ARDUINO_101_AE6642SQ60400T8-if00'
    left = serial.Serial(left_ard, 9600)
    right = serial.Serial(right_ard, 9600)
    left.write(b"s")
    right.write(b"s")
    return



def end():
    "Stops the motors and disconnects the serial comm channels."
    stop()
    right.close()
    left.close()
    return

def stop():
    right.write(b"s")
    left.write(b"s")
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
