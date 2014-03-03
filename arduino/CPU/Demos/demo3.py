import time
import serial
import socket
from uistation import UiStation
ser = serial.Serial('/dev/ttyUSB0')

DEBUG = False
SWITCH = True
UPDATE_PERIOD = 0.05

HOST = ''
PORT = 23331

class State3:
    BEAT_DURATION = 0.05
    BEAT_BPMS = [0, 90, 100, 100, 120, 130, 140, 150, 160,  180]
    BEAT_MODE_MAX = len(BEAT_BPMS)
    

    MAX_FRAME = 10.0
    MIN_FRAME = 0.5
    STEP_FRAME = 0.5
    PAUSE_FRAME_FRACTION = 0.5

    C1 = 255
    C2 = 220
    C3 = 150
    C0 = 0
    COLORS = [ ( C1,  0,  0),
               (  0, C1,  0),
               (  0,  0, C1),
               ( C2, C2,  0),
               (  0, C2, C2),
               ( C2,  0, C2) ]
    NUM_COLORS = len(COLORS)


    def __init__(self, now):
        self.bpm = 90 # (self.MAX_BPM + self.MIN_BPM) / 2
        self.frame_time = 8 # (self.MAX_FRAME + self.MIN_FRAME) / 2
        self.c = [ self.COLORS[2], self.COLORS[0], self.COLORS[1], 
                   self.COLORS[2] , self.COLORS[0]]
        self.c_now = [self.COLORS[0], self.COLORS[1], self.COLORS[2]]
        self.c_start = 0
        self.frame_start = now
        self.frame_end = self.frame_start + self.frame_time
        self.beat_change = now + (60.0 / self.bpm)
        self.beat_on = False
        self.beat_mode = 0

    def resetFrame(self, now):
        self.frame_start = self.frame_end
        self.frame_end = self.frame_start + self.frame_time
        for i in range (1, 4):
            self.c[i] = self.c[i+1]
        self.fixColorVector()

    def fixColorVector(self):
        self.c[0] = self.c[3]
        self.c[4] = self.c[1]

    def blendColor(self, c0, c1, t):
        c2 = [0, 0, 0]
        t2 = min(t/(1.0 - self.PAUSE_FRAME_FRACTION), 1.0)
        for i in range(0, 3):
            c2[i] = (t2*c1[i]) + ((1.0-t2)*c0[i])
        return c2

    def updateColors(self, now):
        while (now > self.frame_end):
            self.resetFrame(now)
        interpolate  = ((now - self.frame_start) /
                        (self.frame_end - self.frame_start))
        interpolate =  max(min(interpolate, 1.0), 0.0)
        for i in range(1, 4):
            self.c_now[i-1] = self.blendColor(self.c[i], self.c[i+1], interpolate)

    def updateBeat(self, now):
        if (self.beat_mode == 0):
            return
        if (now < self.beat_change):
            return
        beat_interval =  (60.0 / self.bpm)
        if (self.beat_on):
            self.beat_change = self.beat_change - self.BEAT_DURATION + beat_interval
            self.beat_on = False
        else:
            print "BEAT"
            self.beat_change = self.beat_change + self.BEAT_DURATION
            self.beat_on = True

    def changeBeatMode(self, up, now):
        # Force the beat on
        self.beat_change = now
        self.beat_on = False
        self.updateBeat(now)

        step = 1
        if (not up):
            step = -1
        self.beat_mode = self.beat_mode + step
        self.beat_mode = max(-self.BEAT_MODE_MAX, self.beat_mode)
        self.beat_mode = min(self.BEAT_MODE_MAX, self.beat_mode)
        self.bpm = self.BEAT_BPMS[abs(self.beat_mode)]
    
    def changeSpeed(self, up):
        step = STEP_FRAME
        if (not up):
            step = -STEP_FRAME
        self.frame_time = min(max(self.frame_time + step, self.MIN_FRAME),
                              self.MAX_FRAME)
  
    def moveColor(self, up):
        r = range(1,4)
        step = 1
        if (not up):
            step = -1
            r.reverse()
        
        for i in r:
            self.c[i] = self.c[i + step]
        self.fixColorVector()

    def changeColor(self, up):
        if (up):
            self.c_start = (self.c_start + 1) % self.NUM_COLORS
        else:
            self.c_start = (self.c_start - 1) % self.NUM_COLORS
        for i in range (0, 3):
            self.c[i+1] = self.COLORS[(self.c_start + i) % self.NUM_COLORS]
        self.fixColorVector()
        

    def update(self, now):
        self.updateColors(now)
        self.updateBeat(now)
        if (self.beat_on and self.beat_mode != 0):
            if (self.beat_mode > 0):
                return [[255,255,255],[255,255,255],[255,255,255]]
            if (self.beat_mode < 0):
                return [[0,0,0],[0,0,0],[0,0,0]]

            factor = 1.0
            if (self.beat_mode > 0):
                factor = 1.1
            if (self.beat_mode < 0):
                factor = 0.9
            for i in range(0,3):
                for j in range(0,3):
                    self.c_now[i][j] = int(min(254, self.c_now[i][j] * factor))
        return self.c_now

def genCommand(led, color):
    b = [0x69, led, 0, 0, 0, 0]
    for i in range(0,3):
        b[2+i] = min(254, max(int(color[i]), 0))
    mval = 0
    for i in range (0,5):
        mval = genChecksum(mval, b[i])
    b[5] = mval & 0xff
    b2 = [str(chr(x)) for x in b]
    return ''.join(b2)

def genChecksum(old, c):
   return c + ((((old & 0x7f) << 1) | ((old & 0x80) >> 7)) & 0xff)
              
     
          

def debugCommand(c):
    return [ord(x) for x in c]

print "hello"
station = None
if SWITCH:
    station=UiStation(HOST,PORT)
    station.update()

if (DEBUG):
    s = State3(0)
    for i in range (0, 210):
        colors = s.update(i/100.0)
        c0 = genCommand(0, colors[0])
        c1 = genCommand(1, colors[1])
        c2 = genCommand(2, colors[2])
        print debugCommand(c0),debugCommand(c1),debugCommand(c2)
else:
    s = State3(time.time())
    print " Entering loop..."
    while(1):
        now = time.time()
        colors = s.update(now)
        #print colors
        if (ser.inWaiting()):
            foo = ser.read()
        cs = []
        for i in range(0,3):
            co = genCommand(i, colors[i])
            ser.write(co)
            cs.append(debugCommand(co))
        print cs
        time.sleep(UPDATE_PERIOD)
        if SWITCH:
            result = station.update() 
            if result:
                for r in result:  
                    if (r == 0):
                        s.moveColor(False)
                    if (r == 1):
                        s.changeColor(False)
                    if (r == 2):
                        s.changeBeatMode(False, now)
                    if (r == 3):
                        s.moveColor(True)
                    if (r == 4):
                        s.changeColor(True)
                    if (r == 5):
                        s.changeBeatMode(True, now)
                    print "Switch ", r

        
