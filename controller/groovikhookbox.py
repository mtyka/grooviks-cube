#!/usr/bin/env python
""" producer.py
Produces random data samples for the EQ sliders.
Uses the Hookbox REST api for publishing the data 
on channel "iframe".

--- License: MIT ---

 Copyright (c) 2010 Hookbox

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.

"""

import copy
import fileinput
import json
import math
import random
import sys
import threading
import time
import datetime
import urllib, urllib2
import display
import serial
import lightboard

import groovik
import hbclient
from glog import GLog
from groovikutils import *
from groovikconfig import *
from GScript import GScript

TARGET_FRAMERATE = 3
TARGET_FRAMETIME = 1.0 / TARGET_FRAMERATE

# 30 looks good on real PCs.  iphones and ipads max out at about 5-10.
# TODO: publish multiple channels at different framerates

# Ensure the cube is only accessed form one thread at a time
cube_lock = threading.Lock()

def compress_datagram(datagram):
    """Returns a JSON object to be sent through hookbox.
    """

    hex_datagram = ''

    for facet in datagram:
        for rgb in facet:
            hexval = "%02x" % (rgb * 255)
            hex_datagram += hexval

    output = '"%s"' % hex_datagram
    #print "sending %s" % output
    return output

last_datagram_sent = None
last_datagram_sent_timestamp = datetime.datetime.now()


def too_long_since_last_datagram():
    """Check if it's been more than a couple of seconds since we sent the last
    datagram.  If not, so, return True.
    This keeps a minimum framerate, which effectively acts as iframes for new clients
    """
    how_long_ago = datetime.datetime.now() - last_datagram_sent_timestamp
    threshhold = datetime.timedelta(0,3) # seconds
    return how_long_ago > threshhold


def push_message(datagram):
    """Pushes a datagram out onto the hookbox channel
    """

    global last_datagram_sent
    global last_datagram_sent_timestamp

    if datagram == last_datagram_sent:
        # In general we don't want to send repeated frames.
        if not too_long_since_last_datagram():
            return
    else:
        last_datagram_sent = datagram

    last_datagram_sent_timestamp = datetime.datetime.now()

    # assume the hookbox server is on localhost:2974    
    url = "http://127.0.0.1:2974/rest/publish"

    values = { "secret" : "bakonv8",
               "channel_name" : "iframe",
               "payload" : []
             }

    values["payload"] = compress_datagram(datagram)
    formdata = urllib.urlencode(values)
    req = urllib2.Request(url, formdata)
    resp = urllib2.urlopen(req)

    # the hookbox response can be useful for debugging,
    # but i'm commenting it out.
    #page = resp.read()
    #print page

class Cube():
    def __init__(self):

        count = 25
        self.displayc = display.Display(count, "input_playa.py" )
        
        # connect to the hookbox client and receive commands
        groovikConfig.SetConfigFileName( 'config_pc.txt' )
        groovikConfig.LoadConfig()

        self.logger = GLog("moves.log");
        self.logger.logLine("[ \"reset\" ]");
        
        self.grooviksCube = groovik.GrooviksCube( self.logger, self.displayc )
        curTime = time.time()
        self.simTime = curTime;
        self.grooviksCube.SetStartTime( curTime )
        
        # simulate one frame so we have a valid state to render on first frame
        # self.simulate()

        client = hbclient.HookClient(self.process_commands)
        client_thread = threading.Thread(target = client.run)
        client_thread.setDaemon(True)
        client_thread.start()

    def process_commands(self, rtjp_frame):
        
        if rtjp_frame[1] == "PUBLISH":
            if rtjp_frame[2]['channel_name'] == 'faceclick':
                rot_command = rtjp_frame[2]['payload'][1:]
                face = rtjp_frame[2]['payload'][0]
                #print rot_command
                with cube_lock:
                    # callbacks for both rotation and pixel click
					# better way of doing this?
                    self.grooviksCube.HandleInput( CubeInput.ROTATION, [rot_command])
                    self.grooviksCube.HandleInput( CubeInput.FACE_CLICK, face)
                    #self.grooviksCube.QueueEffect( "victory0" )
            elif rtjp_frame[2]['channel_name'] == 'gamemode':
                self.logger.logLine( "GameMode: %s " % (rtjp_frame[2]['payload']) )
                depth = rtjp_frame[2]['payload']['difficulty']
                self.grooviksCube.ResetColors()
                self.grooviksCube.Randomize(depth)
            elif rtjp_frame[2]['channel_name'] == 'cubemode':
                self.logger.logLine( "CubeMode: %s " % (rtjp_frame[2]['payload']) )
                mode = rtjp_frame[2]['payload']['mode']
                if( self.grooviksCube.GetCurrentMode() != mode):
                    self.grooviksCube.QueueModeChange(mode)
            elif rtjp_frame[2]['channel_name'] == 'colorcalib':
                command = rtjp_frame[2]['payload']
                self.logger.logLine( "Color calibration: Pixel, (R G B) = %s " % (commmand) )
                with cube_lock:
                    self.grooviksCube.HandleInput( CubeInput.COLOR_CAL, command)
    
    def interpolateFrames( this, data, passedTime, dataLast ):
        if not data:
            return dataLast;
        beforeTime = 0.0
        afterTime = 0.0
        for i in range( len( data ) ):
            beforeTime = afterTime
            afterTime += data[i][0]
            if ( passedTime >= beforeTime and passedTime <= afterTime ):
                if ( i == 0 ):
                    before = dataLast
                else:
                    before = data[i-1][1]
                after = data[i][1]
                if ( len(before) == 0):
                    before = after
                lerpedColors = []
                c = []
                if ( afterTime != beforeTime ):
                    t = ( passedTime - beforeTime ) / ( afterTime - beforeTime )
                else:
                    t = 1.0
                for j in range( 54 ) :
                    c = BlendColorsRGB( before[j], after[j], t )
                    lerpedColors.append( c[:] )
                return lerpedColors
        return dataLast
                
                      
                

    
    def run(self):
        lastFrameLerpedColors = []
        while True:
            self.displayc.loop()

            frameStartTime = time.time()
              
            data = self.simulate()
            # generate random colors for every cube face every 1.5 seconds
            # and publish them via the HTTP/REST api.

            frameLerpedColors = []
            self.simTime = self.simTime + TARGET_FRAMETIME;            
            while ((self.simTime - time.time()) > (TARGET_FRAMETIME/3)):
                # Here we will want to interpolate across the frames, or if there are none use current state.
                frameLerpedColors = self.interpolateFrames( data, time.time()- frameStartTime, lastFrameLerpedColors );
                time.sleep(0.05)
                if ( len(frameLerpedColors) > 0 ):
                    push_message( frameLerpedColors );
            lastFrameLerpedColors = frameLerpedColors
              
    def simulate(self):
        with cube_lock:
          keyframes, resync, rotationStep = self.grooviksCube.Update( self.simTime );
          self.displayc.renderFrames( keyframes, resync )
        if keyframes:
            return keyframes

if __name__ == "__main__":
    cube = Cube()
    cube.run()
