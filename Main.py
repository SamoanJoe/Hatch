"""
Projekt von Salim Boumaouche, Julian Seidel und Robin Schmolke
"""

import RPi.GPIO as gpio
import threading
import time
import RFIDThread as rfid
import Display as display
import Servo as servo
import IRSensor as infrared
import Ultrasound as ultrasound
import PlaySound as sound

#GPIO Pins
CLK = 38
DIO = 40
PWM_DOOR_LOCK = 18
PWM_HATCH = 16
INFRARED_SENSOR = 37
TRIGGER = 35
ECHO = 36
RFID_READER_ONE = 31
RFID_READER_TWO = 29
ALARM_BUTTON = 13
RESET_BUTTON = 15
DOOR_LOCK_BUTTON = 11

#Working hours
CLOSING_TIME = 17
OPENING_TIME = 7

#saves if lock is closed
doorLockOpen = True

#saves if hatch is open
hatchIsOpen = False

#Threading Events
#terminate for closing infinite loops in threads
alarmTerminate = threading.Event()
rfidTerminate = threading.Event()
displayTerminate = threading.Event()
rfidCloseHatch = threading.Event()
technicianEvent = threading.Event()

correctPassword = threading.Event()
wrongPassword = threading.Event()
rfidPasswordLock = threading.Lock()

#only alarm
def alarm(alarmThread):
    alarmThread.start()
    print("alarm is active")

#starts alarm with opening hatch for fire alarm
def alarmWithHatch(alarmThread,PWM_HATCH):
    alarm(alarmThread)
    global hatchIsOpen
    if(not hatchIsOpen):
        servo.openHatch(PWM_HATCH)   
        hatchIsOpen = True
    print("hatch open")

#opens hatch, starts timer, 
def hatchWithDisplay(CLK,DIO,PWM_HATCH,INFRARED_SENSOR,RESET_BUTTON,displayTerminate,rfidCloseHatch,technicianEvent): 
    global hatchIsOpen
    if(not hatchIsOpen):
        sound.hatchOpens()
        servo.openHatch(PWM_HATCH)   
        hatchIsOpen = True
    print("hatch open")
    #starts display with timer
    display.display(CLK, DIO, displayTerminate)
    #emergencies get an earlier exit
    if(displayTerminate.is_set() and not rfidCloseHatch.is_set()):
        return
    #In case of people in front the hatch. The hatch will not close
    if(infrared.isObstacle(INFRARED_SENSOR)):
        print("someone is in the way")
        sound.clearHatch()
        time.sleep(2)
        if(infrared.isObstacle(INFRARED_SENSOR)):
            print("someone is in the way")
            sound.clearHatch()
            time.sleep(2)
            if(infrared.isObstacle(INFRARED_SENSOR)):
                print("technician needed")
                sound.technicianNeeded()
                while True:
                    #wait for technician through reset button or ctrl + c
                    if(technicianEvent.is_set() or gpio.input(RESET_BUTTON)):
                        return
    if(hatchIsOpen):
        sound.hatchCloses()
        servo.closeHatch(PWM_HATCH)
        hatchIsOpen = False
    #if hatch does not close correctly, it will try again
    if(not ultrasound.isHatchInPlace(TRIGGER, ECHO,pin_numbering_mode)):
        print("hatch is not in place")
        sound.clearHatch()        
        if(not hatchIsOpen):
            sound.hatchOpens()
            servo.openHatch(PWM_HATCH)   
            hatchIsOpen = True
        time.sleep(1)
        if(hatchIsOpen):
            sound.hatchCloses()
            servo.closeHatch(PWM_HATCH)
            hatchIsOpen = False
        if(not ultrasound.isHatchInPlace(TRIGGER, ECHO,pin_numbering_mode)):
            print("hatch is not in place")
            sound.clearHatch()
            if(not hatchIsOpen):
                sound.hatchOpens()
                servo.openHatch(PWM_HATCH)   
                hatchIsOpen = True
            print("need a technician")
            sound.technicianNeeded()
            while True:
                #wait for technician through reset button or ctrl + c
                if(technicianEvent.is_set() or gpio.input(RESET_BUTTON)):
                    return
    print("hatch closed")
     

def waitForThreads(alarmThread,rfidThread,displayThread):
    #terminate all living threads
    if(rfidThread.is_alive()):
        rfidTerminate.set()
        rfidThread.join()
        print("rfid is terminated")
    if(alarmThread.is_alive()):
        alarmTerminate.set()
        alarmThread.join()
        print("alarm is terminated")
    if(displayThread.is_alive()):
        displayTerminate.set()
        technicianEvent.set()
        displayThread.join()
        print("display is terminated")
    print("Threads are joined")

if __name__ == "__main__":
    #setup gpio
    pin_numbering_mode = gpio.BOARD
    gpio.setmode(pin_numbering_mode)
    gpio.setup(CLK,gpio.OUT)
    gpio.setup(DIO,gpio.OUT)
    gpio.setup(PWM_HATCH,gpio.OUT)
    gpio.setup(PWM_DOOR_LOCK,gpio.OUT)
    gpio.setup(INFRARED_SENSOR,gpio.IN)
    gpio.setup(TRIGGER, gpio.OUT)
    gpio.setup(ECHO, gpio.IN)
    gpio.setup(RFID_READER_ONE, gpio.OUT)
    gpio.setup(RFID_READER_TWO, gpio.OUT)
    gpio.setup(ALARM_BUTTON, gpio.IN)
    gpio.setup(RESET_BUTTON, gpio.IN) 
    gpio.setup(DOOR_LOCK_BUTTON, gpio.IN)
    try:
        print("setup rdy")
        #rfid thread with 2 rfid readers
        rfidThread = threading.Thread(target=rfid.cardReader,args=(RFID_READER_ONE,RFID_READER_TWO,rfidTerminate,pin_numbering_mode,correctPassword,wrongPassword,rfidPasswordLock))
        rfidThread.start()
        print("rfid is active")
        alarmThread = threading.Thread(target=sound.fireAlarm, args=(alarmTerminate,))
        displayThread = threading.Thread(target=hatchWithDisplay,args=(CLK,DIO,PWM_HATCH,INFRARED_SENSOR,RESET_BUTTON,displayTerminate,rfidCloseHatch,technicianEvent))
        while True:
            #get the hour of system time or external button for testing
            if(int(time.strftime("%H"))>=CLOSING_TIME or (gpio.input(DOOR_LOCK_BUTTON) and not alarmThread.is_alive())):
                if(displayThread.is_alive()):
                    displayTerminate.set()
                    displayThread.join()
                    displayTerminate.clear()
                    displayThread = threading.Thread(target=hatchWithDisplay,args=(CLK,DIO,PWM_HATCH,INFRARED_SENSOR,RESET_BUTTON,displayTerminate,rfidCloseHatch,technicianEvent))
                if(hatchIsOpen):
                    sound.hatchCloses()
                    servo.closeHatch(PWM_HATCH)
                    hatchIsOpen = False
                time.sleep(2)
                sound.lockCloses()
                servo.closeDoorLock(PWM_DOOR_LOCK)
                doorLockOpen = False
                #rfid thread is not needed while waiting
                if(rfidThread.is_alive()):
                    rfidTerminate.set()
                    rfidThread.join()
                    print("rfid thread is termianted")
                time.sleep(3)
                #wait for door to be open again
                while True:
                    timeInHours = int(time.strftime("%H"))
                    print("It is now ", timeInHours, " wait until 7 for the door to open again")
                    if((timeInHours>=OPENING_TIME and timeInHours <CLOSING_TIME) or gpio.input(DOOR_LOCK_BUTTON)):
                        sound.lockOpens()
                        servo.openDoorLock(PWM_DOOR_LOCK)
                        doorLockOpen = True
                        time.sleep(2)
                        #start thread again
                        rfidTerminate.clear()
                        rfidThread = threading.Thread(target=rfid.cardReader,args=(RFID_READER_ONE,RFID_READER_TWO,rfidTerminate,pin_numbering_mode,correctPassword,wrongPassword,rfidPasswordLock))
                        rfidThread.start()
                        print("rfid thread started")
                        break
                    time.sleep(1)
                time.sleep(3)
            #fire alarm button
            elif(gpio.input(ALARM_BUTTON)):
                alarmWithHatch(alarmThread,PWM_HATCH)
                if(displayThread.is_alive()):
                    displayTerminate.set()
                    displayThread.join()
                    print("display is terminated")
                time.sleep(3)
            #reset button and acts as technician
            elif(gpio.input(RESET_BUTTON)):
                if(alarmThread.is_alive()):
                    alarmTerminate.set()
                    alarmThread.join()
                    print("alarm is terminated")
                if(displayThread.is_alive()):
                    displayTerminate.set()
                    technicianEvent.set()
                    displayThread.join()
                    print("display is terminated")
                if(not doorLockOpen):
                    servo.openDoorLock(PWM_DOOR_LOCK)
                    doorLockOpen = True
                    time.sleep(1)
                if(hatchIsOpen):
                    servo.closeHatch(PWM_HATCH)
                    hatchIsOpen = False
                print("hatch closed")
                #make threads free again for use again
                alarmTerminate.clear()
                displayTerminate.clear()
                alarmThread = threading.Thread(target=sound.fireAlarm, args=(alarmTerminate,))
                displayThread = threading.Thread(target=hatchWithDisplay,args=(CLK,DIO,PWM_HATCH,INFRARED_SENSOR,RESET_BUTTON,displayTerminate,rfidCloseHatch,technicianEvent))
                time.sleep(3)
            #wrong password plays a sound
            elif(wrongPassword.is_set()):
                rfidPasswordLock.acquire()
                sound.negativeBeep()
                wrongPassword.clear()
                rfidPasswordLock.release()
            #correct password opens hatch with a 10 min. timer but shortend down for testing
            #correct password again closes door and shuts down timer
            elif(correctPassword.is_set()):
                rfidPasswordLock.acquire()
                if(displayThread.is_alive()):
                    rfidCloseHatch.set()
                    displayTerminate.set()
                    displayThread.join()
                    displayTerminate.clear()
                    rfidCloseHatch.clear()
                else:
                    displayThread = threading.Thread(target=hatchWithDisplay,args=(CLK,DIO,PWM_HATCH,INFRARED_SENSOR,RESET_BUTTON,displayTerminate,rfidCloseHatch,technicianEvent))
                    displayThread.start()
                correctPassword.clear()
                rfidPasswordLock.release()
            #ultrasound sensor for distance measurement is only need when nothing else happens
            elif(not alarmThread.is_alive() and not displayThread.is_alive()):
                if(ultrasound.isHatchInPlace(TRIGGER, ECHO,pin_numbering_mode)):
                    print("hatch is in place")
                else:
                    print("hatch is not in place")
                    #intruder alarm without opening the hatch
                    alarm(alarmThread)
            time.sleep(1)
    except KeyboardInterrupt:
        #stopping everything with ctrl + c
        print("Programm wird abgebrochen")
        waitForThreads(alarmThread,rfidThread,displayThread)
        time.sleep(1)
        #get everything to default position
        if(not doorLockOpen):
            servo.openDoorLock(PWM_DOOR_LOCK)
            time.sleep(1)
        if(hatchIsOpen):
            servo.closeHatch(PWM_HATCH)
            hatchIsOpen = False
    except Exception as e:
        #for debugging other exception from threads
        print("unknown exception")
        print(e)
        waitForThreads(alarmThread,rfidThread,displayThread)
    finally:
        #cleanup at the end
        gpio.cleanup()
        print("I did the cleanup")