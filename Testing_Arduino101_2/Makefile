LEFT_PORT=/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_6493833393235151C131-if00
RIGHT_PORT=/dev/serial/by-id/usb-Arduino_LLC__www.arduino.cc__Genuino_Uno_85531303631351112162-if00
BOARD_TYPE=arduino:avr:uno
COMPILE=arduino --verify --preserve-temp-files
UPLOAD=arduino --upload
MAIN=Testing_Arduino101_2.ino
SOURCES=$(MAIN) Gyroscope.ino CapacitanceSensor.ino Motors.ino Commands.ino Servos.ino Encoders.ino UltrasonicSensors.ino

all: verify upload_left upload_right

verify: $(SOURCES)
	$(COMPILE) --board $(BOARD_TYPE) $(MAIN)

upload_left: verify
	$(UPLOAD) --board $(BOARD_TYPE) --port $(LEFT_PORT) $(MAIN)

upload_right: verify
	$(UPLOAD) --board $(BOARD_TYPE) --port $(RIGHT_PORT) $(MAIN)
