import wave
import pygame

#infinite until event
def fireAlarm(alarmTerminate): 
    pygame.mixer.init()
    pygame.mixer.music.load("Alarm.wav")
    pygame.mixer.music.play(-1)
    print("Alarm is playing")
    while True:
        if(alarmTerminate.is_set()):
            pygame.mixer.music.pause()
            print("alarm is paused")
            return

def oneMin(): 
    pygame.mixer.init()
    pygame.mixer.music.load("1min.wav")
    pygame.mixer.music.play()
    print("1min is playing")

def threeMin():
    pygame.mixer.init()
    pygame.mixer.music.load("3min.wav")
    pygame.mixer.music.play()
    print("3min is playing")

def fiveMin():
    pygame.mixer.init()
    pygame.mixer.music.load("5min.wav")
    pygame.mixer.music.play()
    print("5min is playing")

#wait for finish
def clearHatch():
    pygame.mixer.init()
    pygame.mixer.music.load("clearHatch.wav")
    pygame.mixer.music.play()
    print("clear Hatch is playing")
    while pygame.mixer.music.get_busy() == True:
        continue

#wait for finish
def hatchOpens():
    pygame.mixer.init()
    pygame.mixer.music.load("hatchOpens.wav")
    pygame.mixer.music.play()
    print("hatch opens is playing")
    while pygame.mixer.music.get_busy() == True:
        continue

#wait for finish
def hatchCloses():
    pygame.mixer.init()
    pygame.mixer.music.load("hatchCloses.wav")
    pygame.mixer.music.play()
    print("hatch closes is playing")
    while pygame.mixer.music.get_busy() == True:
        continue

#wait for finish
def lockCloses():
    pygame.mixer.init()
    pygame.mixer.music.load("lockCloses.wav")
    pygame.mixer.music.play()
    print("lock closes is playing")
    while pygame.mixer.music.get_busy() == True:
        continue

#wait for finish
def lockOpens():
    pygame.mixer.init()
    pygame.mixer.music.load("lockOpens.wav")
    pygame.mixer.music.play()
    print("lock opens is playing")
    while pygame.mixer.music.get_busy() == True:
        continue

#wait for finish
def negativeBeep():
    pygame.mixer.init()
    pygame.mixer.music.load("negative_beep.wav")
    pygame.mixer.music.play()
    print("negative beep is playing")
    while pygame.mixer.music.get_busy() == True:
        continue

#wait for finish
def technicianNeeded():
    pygame.mixer.init()
    pygame.mixer.music.load("technicianNeeded.wav")
    pygame.mixer.music.play()
    print("technician needed is playing")
    while pygame.mixer.music.get_busy() == True:
        continue