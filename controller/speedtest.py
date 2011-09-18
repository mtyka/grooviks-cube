#imports 

#import standard libraries
import fileinput
import time
import socket
import sys
import traceback

#import uistation;


#import extensions
import serial

#import our own binaries
import groovik
import lightboard
import display


import sys;

def returnIDForPort(port, baud):
	m = lightboard.Message();
	r = m.createFromQuantizedPixelList(0, [[200,0,0], [200,0,0], [200,0,0], [200,0,0], [200,0,0] ])
	g = m.createFromQuantizedPixelList(0, [[0,200,0], [0,200,0], [0,200,0], [0,200,0], [0,200,0] ])
	b = m.createFromQuantizedPixelList(0, [[0,0,200], [0,0,200], [0,0,200], [0,0,200], [0,0,200] ])

	lb = lightboard.LightBoardTracker();
	lb.openSerialSpeed(port, baud);
	lb.ser.write(r);
	time.sleep(2.0);
	lb.read();
	print lb.lastgood.guid 


def runLoopTest(port, baud):   
	m = lightboard.Message();
	r = m.createFromQuantizedPixelList(0, [[200,0,0], [200,0,0], [200,0,0], [200,0,0], [200,0,0] ])
	g = m.createFromQuantizedPixelList(0, [[0,200,0], [0,200,0], [0,200,0], [0,200,0], [0,200,0] ])
	b = m.createFromQuantizedPixelList(0, [[0,0,200], [0,0,200], [0,0,200], [0,0,200], [0,0,200] ])

	lb = lightboard.LightBoardTracker();
	lb.openSerialSpeed(port, baud);
	c = 0;
        cDropped = 0;
        
	for i in range(1000):
	  print "Top of loop, iteration: " 
	  print i;
          c = c + 1;
	  lb.ser.write(r);
	  lb.read();
          print lb.lastgood;
	  #if (lb.lastgood.pixels[0][0] != 200):
	  #	cDropped = cDropped + 1;
          c = c + 1;
	  lb.ser.write(g);
	  lb.read();
	  #if (lb.lastgood.pixels[0][1] != 200):
	  #	cDropped = cDropped + 1;          
	  c = c + 1;
	  lb.ser.write(b);
	  lb.read();
	  #if (lb.lastgood.pixels[0][2] != 200):
	  #	cDropped = cDropped + 1;   
	  
	  #print "c: " + c + " cDropped: " + cDropped;	
