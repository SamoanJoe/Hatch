import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
try:
    text = input("Was soll gespeichert werden? ")
    print("Dranhalten")
    reader.write(text)
    print("Fertig")
finally:
    GPIO.cleanup()