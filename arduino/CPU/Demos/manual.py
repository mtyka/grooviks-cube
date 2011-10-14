# connect to gumstix: screen /dev/tty.usbserial-A80098YY 115200
import time
import socket
import serial
from colorLooper import colorLooper

HOST = ''                 # Symbolic name meaning the local host
PORT = 23331              # Arbitrary non-privileged port

ser = serial.Serial('/dev/ttyUSB0', 9600)
result = None

ser.write("\000\000\000\000\000")
ser.write("\000\001\000\000\000")
ser.write("\000\002\000\000\000")
ser.write("\000\003\000\000\000")

while 1:
    inp = raw_input()
    rgb = inp.split(',')
    if (len(rgb) != 3):
        print "Wrong input: ", inp
        continue
    r = 0
    g = 0
    b = 0
    try:
        r = int(rgb[0])
        g = int(rgb[1])
        b = int(rgb[2])
    except:
        print "Not integers: ", rgb
        continue
    s = "%c%c%c%c%c" % (0,0,r,g,b)
    print "Setting to: ", r,g,b
    ser.write(s)
    time.sleep(0.001)
