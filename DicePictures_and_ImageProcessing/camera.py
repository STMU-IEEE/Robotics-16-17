from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
sleep(5)
#camera.capture('/home/pi/Desktop/image.jpg')
camera.contrast = 100
sleep(5)
camera.stop_preview()
