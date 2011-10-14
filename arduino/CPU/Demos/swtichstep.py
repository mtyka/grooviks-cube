# connect to gumstix: screen /dev/tty.usbserial-A80098YY 115200
import time
import socket
import serial
from colorLooper import colorLooper
from uistation import UiStation

HOST = ''                 # Symbolic name meaning the local host
PORT = 23331              # Arbitrary non-privileged port
debug = True
switch = True

station = None
if switch:
    station = UiStation(HOST, PORT)
ser = serial.Serial('/dev/ttyUSB0', 9600)
cl = colorLooper()
lastChangeTime = 0
count = 0
result = None

ser.write("\000\000\000\000\000")
ser.write("\000\001\177\077\177")
ser.write("\000\002\277\277\277")
ser.write("\000\003\377\377\377")

strs = [  "\000\000\000\000\100",  
          "\000\000\377\000\100",
          "\000\000\000\377\000",
          "\000\000\377\377\077",
          "\000\000\377\000\377",
          "\000\000\000\377\377",
          "\000\000\377\377\377"]
while 1:
    if (station):
        result = station.update()
    if (result or time.time() -  lastChangeTime  > 3.0):
        count = (count + 1) % len(strs)
        ser.write(strs[count])
        lastChangeTime = time.time()
    time.sleep(0.001)
