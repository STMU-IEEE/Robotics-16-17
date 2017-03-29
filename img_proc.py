# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import argparse
import cv2
import numpy as np

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

def nothing(x):
    pass
# cv2.namedWindow('Sliders')
# cv2.createTrackbar('H Min', 'Sliders',0,255,nothing)
# cv2.createTrackbar('H Max', 'Sliders',0,255,nothing)
# cv2.createTrackbar('S Min', 'Sliders',0,255,nothing)
# cv2.createTrackbar('S Max', 'Sliders',0,255,nothing)
# cv2.createTrackbar('V Min', 'Sliders',0,255,nothing)
# cv2.createTrackbar('V Max', 'Sliders',0,255,nothing)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # show the frame
    # cv2.imshow("hsv", hsv)
    key = cv2.waitKey(1) & 0xFF

    kernel = np.ones((5,5), np.uint8)
    # define range of blue color in HSV
    # h_min = cv2.getTrackbarPos('H Min', 'Sliders')
    # s_min = cv2.getTrackbarPos('S Min', 'Sliders')
    # v_min = cv2.getTrackbarPos('V Min', 'Sliders')
    # lower_blue = np.array([h_min, s_min, v_min])
    #
    # h_max = cv2.getTrackbarPos('H Max', 'Sliders')
    # s_max = cv2.getTrackbarPos('S Max', 'Sliders')
    # v_max = cv2.getTrackbarPos('V Max', 'Sliders')
    #
    # upper_blue = np.array([h_max, s_max, v_max])

    # Threshold the HSV image to get only blue colors
    # mask = cv2.inRange(hsv, lower_blue, upper_blue)
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help = "path to the image file")
    args = vars(ap.parse_args())
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

    # sm_copy = shapeMask.copy()
    # (cnts, _) = cv2.findContours(sm_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow('Mask 1',shapeMask3)
    cv2.imshow('Mask 2',shapeMask2)
    # cv2.imshow('res',res)

    cnts = cv2.findContours(shapeMask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print ("I found " + str(len(cnts)) + " dots!")
    key = cv2.waitKey(5) & 0xFF


	# clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
       break


"""
import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)

    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
"""
