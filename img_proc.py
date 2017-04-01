# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import argparse
import cv2
import numpy as np


def nothing(x):
    pass

def dotCount():

    # initialize the camera and grab a reference to the raw camera capture
    WIDTH = 1024
    HEIGHT = 1024
    camera = PiCamera()
    camera.resolution = (WIDTH, HEIGHT)
    camera.framerate = 2
    rawCapture = PiRGBArray(camera, size=(WIDTH, HEIGHT))
    h_min = 0
    h_max = 255
    s_min = 0
    s_max = 255
    v_min = 0
    v_max = 255

    # allow the camera to warmup
    time.sleep(0.1)

    vals = np.zeros(25, np.uint8)
    frameCount = 0
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # show the frame
        # cv2.imshow("hsv", hsv)
        key = cv2.waitKey(1) & 0xFF

        kernel = np.ones((5,5), np.uint8)

        lower = np.array([0, 0, 133])
        upper = np.array([255, 255, 255])
        shapeMask = cv2.inRange(image, lower, upper)
        shapeMask2 = cv2.dilate(shapeMask, kernel, iterations=12)
        shapeMask3 = cv2.erode(shapeMask2, kernel, iterations=12)

        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(image,image, mask=shapeMask3)
        lower = np.array([0, 0, 0])
        upper = np.array([255, 255, 133])
        shapeMask = cv2.inRange(image, lower, upper)
        shapeMask2 = cv2.bitwise_and(shapeMask,shapeMask,mask=shapeMask3)
        shapeMask2 = cv2.erode(shapeMask2, kernel, iterations = 4)
        shapeMask2 = cv2.dilate(shapeMask2, kernel, iterations = 4)

        _, cnts, _ = cv2.findContours(shapeMask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print ("I found " + str(len(cnts)) + " dots!")
        vals[frameCount] = len(cnts)
        if frameCount > 50:
            break

    vals = sorted(vals)
    output = vals[12]
    return output
