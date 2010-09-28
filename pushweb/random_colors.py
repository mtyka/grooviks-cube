#!/usr/bin/env python
""" producer.py
Produces random data samples for the EQ sliders.
Uses the Hookbox REST api for publishing the data 
on channel "chan1".

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


def push_message(datagram):

    # assume the hookbox server is on localhost:2974    
    url = "http://127.0.0.1:2974/rest/publish"

    values = { "secret" : "bakonv8",
               "channel_name" : "iframe",
               "payload" : []
             }

    values["payload"] = json.dumps(datagram)
    formdata = urllib.urlencode(values)
    req = urllib2.Request(url, formdata)
    resp = urllib2.urlopen(req)

    # the hookbox response can be useful for debugging,
    # but i'm commenting it out.
    #page = resp.read()
    #print page


def main ():

    faceColors = [ [ 0.0, 1.0, 0.0 ], [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0] ]

    while True:
        # generate random colors for every cube face every 1.5 seconds
        # and publish them via the HTTP/REST api.
        data = [ random.sample(faceColors, 1)[0] for x in range (0,54) ]
        push_message( data )
        print data
        time.sleep(1.5)
                


if __name__ == "__main__":
    main()