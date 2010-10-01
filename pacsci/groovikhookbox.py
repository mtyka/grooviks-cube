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

import time, urllib, urllib2, json, random

import sys
import math
import time
import fileinput
import groovik
import copy
from groovikutils import *
from GScript import GScriptLibrary;
from GScript import GScript
from glog import GLog;
from groovikconfig import *



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





def push_message(datagram):
    """Pushes a datagram out onto the hookbox channel
    """

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

def simulate( grooviksCube ):
    simTime = time.time()
    keyframes, resync = grooviksCube.Update( simTime )
    if keyframes:
        return keyframes

def main ():
    groovikConfig.SetConfigFileName( 'config_pc.txt' )
    groovikConfig.LoadConfig()

    moveLogger = GLog("moves.log");
    moveLogger.logLine("[ \"reset\" ]");
    
    grooviksCube = groovik.GrooviksCube( moveLogger )
    curTime = time.time()
    grooviksCube.SetStartTime( curTime )
    
    # simulate one frame so we have a valid state to render on first frame
    simulate(grooviksCube)

    while True:
        # generate random colors for every cube face every 1.5 seconds
        # and publish them via the HTTP/REST api.
        if grooviksCube.IsIdle():
          #pass
          #grooviksCube.QueueRotation([[random.randrange(0,9), random.choice([True,False])]])
          grooviksCube.QueueEffect( "victory0" )

        data = simulate(grooviksCube)
        if data:
            frame = data[-1][1]
            push_message( frame )
            time.sleep(.033333333)

if __name__ == "__main__":
    main()
