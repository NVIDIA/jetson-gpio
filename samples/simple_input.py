# ------------------------------------------------------------------------------
# Name         : JetsonMotorInterface.py
# Date Created : 2/22/2021
# Author(s)    : Micheal Caracciolo, Chris Lloyd, Owen Casciotti
# Github Link  : https://github.com/michealcarac/VSLAM-Mapping
# Description  : A class to control a STM (CDL=> Add model here) microcontroller
#                Controlling two stepper motors with individual (CDL=>
#                Add Motor controller model here) motor controller boards.
# ------------------------------------------------------------------------------

# External Imports
import RPi.GPIO as GPIO  # For interfacing with the Jetson GPIO
import time              # CDL=> Needed?

# Jetson version (Change here for different boards)
JETSON_BOARD_NAME = "NANO"  # AGX or NANO

# Pin Definitons: (BOARD pin notation)
if (JETSON_BOARD_NAME == "NANO"):  # For Jetson Nano
	FORWARDS_PIN    = 37
	BACKWARDS_PIN   = 35
	LEFT_PIN        = 38
	RIGHT_PIN       = 36
	JETSON_CTRL_PIN = 32
elif (JETSON_BOARD_NAME == "AGX"):  # For Jetson AGX
	# FORWARDS_PIN    = 37 # CDL=> Find value
	# BACKWARDS_PIN   = 35 # CDL=> Find value
	# LEFT_PIN        = 38 # CDL=> Find value
	# RIGHT_PIN       = 36 # CDL=> Find value
	# JETSON_CTRL_PIN = 32 # CDL=> Find value
else
	print("Unsupported Jetson board!")

def initPins():
	"""
	Setup the Jetson GPIO pins for motor control.
	"""
	GPIO.setmode(GPIO.BOARD)                  # BOARD pin-numbering scheme
	GPIO.setup(FORWARDS_PIN,    GPIO.OUT)
	GPIO.setup(BACKWARDS_PIN,   GPIO.OUT)
	GPIO.setup(LEFT_PIN,        GPIO.OUT)
	GPIO.setup(RIGHT_PIN,       GPIO.OUT)
	GPIO.setup(JETSON_CTRL_PIN, GPIO.IN)
	stopMotors()                              # Init with motors stopped

# ------------------------------------------------------------------------------
# High level user control of motors
# ------------------------------------------------------------------------------
def stopMotors():
	GPIO.output(FORWARDS_PIN,  GPIO.LOW)
	GPIO.output(BACKWARDS_PIN, GPIO.LOW)
	GPIO.output(LEFT_PIN,      GPIO.LOW)
	GPIO.output(RIGHT_PIN,     GPIO.LOW)

def goForwards():
	GPIO.output(FORWARDS_PIN,  GPIO.HIGH)
	GPIO.output(BACKWARDS_PIN, GPIO.LOW)
	GPIO.output(LEFT_PIN,      GPIO.LOW)
	GPIO.output(RIGHT_PIN,     GPIO.LOW)

def goBackwards():
	GPIO.output(FORWARDS_PIN,  GPIO.LOW)
	GPIO.output(BACKWARDS_PIN, GPIO.HIGH)
	GPIO.output(LEFT_PIN,      GPIO.LOW)
	GPIO.output(RIGHT_PIN,     GPIO.LOW)

def turnLeft():
	GPIO.output(FORWARDS_PIN,  GPIO.LOW)
	GPIO.output(BACKWARDS_PIN, GPIO.LOW)
	GPIO.output(LEFT_PIN,      GPIO.HIGH)
	GPIO.output(RIGHT_PIN,     GPIO.LOW)

def turnRight():
	GPIO.output(FORWARDS_PIN,  GPIO.LOW)
	GPIO.output(BACKWARDS_PIN, GPIO.LOW)
	GPIO.output(LEFT_PIN,      GPIO.LOW)
	GPIO.output(RIGHT_PIN,     GPIO.HIGH)

# Main code for this file. Only runs if this file is the top file
if __name__ == "__main__":
	print("Init GPIO interface")
	initPins()

	print("Moving forwards for 5 seconds!")
	goForwards()
	time.sleep(5)

	print("Rotate left for 5 seconds!")
	turnLeft()
	time.sleep(5)

	print("Stop motors!")
	stopMotors() 
