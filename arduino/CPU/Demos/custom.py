# connect to gumstix: screen /dev/tty.usbserial-A80098YY 115200
import time
import socket
import serial
from colorLooper import colorLooper
from uistation import UiStation

HOST = ''                 # Symbolic name meaning the local host
PORT = 23331              # Arbitrary non-privileged port

debug = True


station = UiStation(HOST, PORT)
ser = serial.Serial('/dev/ttyUSB0', 9600)
cl = colorLooper()
lastChangeTime = 0
while 1:
    result = station.update()
    if (result != None):
        cl.incBlue()
    if (time.time() -  lastChangeTime  > 1.0):
        cl.gotoNextColor()
        s = cl.getColorString(0)
        ser.write(s)
        lastChangeTime = time.time()
    time.sleep(0.001)

pressCount = 0
count =0
lastKeepAliveTime = time.time()
strs = [ "\000\003\000\000\000", "\000\000\077\077\177",  
         "\000\000\000\000\000", "\000\001\077\077\177",
         "\000\001\000\000\000", "\000\002\077\077\177",
         "\000\002\000\000\000", "\000\003\077\077\177"]


while 1:
    results = station.update()
    if results != None:
        print "(%4d) Pressed:" % count , results
        count = count + 1
        sid = count % 4
        ser.write(strs[sid*2])
        ser.write(strs[sid*2 + 1])
    #time.sleep(2.1)
    #if (time.time() - lastKeepAliveTime > 1.0):
    #    print "."
