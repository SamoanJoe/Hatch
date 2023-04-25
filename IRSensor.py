import RPi.GPIO as GPIO

#true if there is an object
def isObstacle(infraredPin):
    return not GPIO.input(infraredPin)