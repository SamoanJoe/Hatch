import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522
import time
import spidev

class NFC():
    def __init__(self, bus=0, device=0, spd=1000000):
        self.reader = SimpleMFRC522()
        self.close()
        self.boards = {}
        
        self.bus = bus
        self.device = device
        self.spd = spd

    def reinit(self):
        self.reader.READER.spi = spidev.SpiDev()
        self.reader.READER.spi.open(self.bus, self.device)
        self.reader.READER.spi.max_speed_hz = self.spd
        self.reader.READER.MFRC522_Init()

    def close(self):
        self.reader.READER.spi.close()

    def addBoard(self, rid, pin):
        self.boards[rid] = pin

    def selectBoard(self, rid):
        if not rid in self.boards:
            print("readerid " + rid + " not found")
            return False

        for loop_id in self.boards:
            gpio.output(self.boards[loop_id], loop_id == rid)
        return True

    def read(self, rid):
        if not self.selectBoard(rid):
            return None

        self.reinit()
        cid, val = self.reader.read_no_block()
        self.close()

        return cid,val

    def write(self, rid, value):
        if not self.selectBoard(rid):
            return False

        self.reinit()
        self.reader.write_no_block(value)
        self.close()
        return True


def cardReader(reader1Pin, reader2Pin, rfidTerminate, pin_numbering_mode, correctPassword, wrongPassword, rfidPasswordLock):
    gpio.setmode(pin_numbering_mode)
    #init reader
    nfc = NFC()
    nfc.addBoard("reader1",reader1Pin)
    nfc.addBoard("reader2",reader2Pin)
    #use reader
    cid1,cid2 =(None,None)
    data1,data2=("","")
    print("init done")
    while True:
        time.sleep(5)
        while not cid1 and not cid2 and not rfidTerminate.is_set():
            print("I'm reading")
            cid2, data2 = nfc.read("reader2")
            time.sleep(0.4)
            cid1, data1= nfc.read("reader1")
            time.sleep(0.4)
        if(rfidTerminate.is_set()):
            return
        print("found")
        if cid1:
            print(data1)
        if cid2:
            print(data2)
        #reader had invisible characters
        if(str(data1).strip() == "password".strip() or str(data2).strip() == "password".strip()):
            print("correct input")
            rfidPasswordLock.acquire()
            correctPassword.set()
            rfidPasswordLock.release()
        else:
            print("wrong input")
            rfidPasswordLock.acquire()
            wrongPassword.set()
            rfidPasswordLock.release()
        cid1,cid2 =(None,None)