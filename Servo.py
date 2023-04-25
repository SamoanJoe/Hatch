import RPi.GPIO as GPIO
import time
import PlaySound as sound

def openHatch(hatchPin):
    # Create PWM instance on the servo Pin with a frequency of 50Hz
    pwmHatch = GPIO.PWM(hatchPin, 50)

    # Start PWM with a duty cycle of 7.5% (neutral position for most servos)
    pwmHatch.start(5)
    time.sleep(1)
    pwmHatch.ChangeDutyCycle(2.5)
    time.sleep(1)

def closeHatch(hatchPin):
    # Create PWM instance on the servo Pin with a frequency of 50Hz
    pwmHatch = GPIO.PWM(hatchPin, 50)

    # Start PWM with a duty cycle of 7.5% (neutral position for most servos)
    pwmHatch.start(5)
    time.sleep(1)
    pwmHatch.ChangeDutyCycle(7.5)
    time.sleep(1)

def openDoorLock(doorLockPin):
    # Create PWM instance on the servo Pin with a frequency of 50Hz
    pwmDoorLock = GPIO.PWM(doorLockPin, 50)

    # Start PWM with a duty cycle of 7.5% (neutral position for most servos)
    pwmDoorLock.start(12.5)
    time.sleep(1)

def closeDoorLock(doorLockPin):
    # Create PWM instance on the servo Pin with a frequency of 50Hz
    pwmDoorLock = GPIO.PWM(doorLockPin, 50)

    # Start PWM with a duty cycle of 7.5% (neutral position for most servos)
    pwmDoorLock.start(2.5)
    time.sleep(1)