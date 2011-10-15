#imports 

#import standard libraries
import fileinput
import time
import socket

#import uistation;
from uistation import UiStation
from UIManager import UIManager;

#import extensions
import serial

#import our own binaries
import groovik
import lightboard
import display

from uistation import UiStation

import sys;

plat = sys.platform.lower()
count = 25;
if   plat[:5] == 'linux':
   count = 11;

ui = UIManager();
display = display.Display(count, "input2.py");

time.sleep(5);
    
lasttime = time.time();

grooviksCube = groovik.GrooviksCube();
grooviksCube.SetStartTime( time.clock() );


cFrames = 0;
timeStart = time.time();

iPixel = 0;

while(True):
   now = time.time();
   if (now - timeStart > 2):
      print "Framerate";
      print cFrames / (now - timeStart);
      cFrames = 0;
      timeStart = now;
      
   #sample the input
   result = ui.update();
   if result:
      command = result[0];
      # if this is a rotation...
      if (command < 18):
         rot = command / 2;
         reverse = command % 2;
         print "queuing rotation";
         #grooviksCube.QueueRotation( rot, reverse );
         iPixel += 1;
         if (iPixel == 54):
            iPixel = 0;
         
   #handle any display management 
   display.loop();
      
   #throttle the frame-rate
   if (time.time() - lasttime > .2):
      cFrames = cFrames + 1;
      # run the simmulation
      grooviksCube.Update( time.clock() )  
      colors = grooviksCube.GetColors();
      for i in range(54):
         display.setPixel(i, lightboard.Pixel(int(colors[i][0] * 255), int(colors[i][1] * 255), int(colors[i][2] * 255)));
      
      display.setPixel(iPixel, lightboard.Pixel( 255, 0, 255 ));
      
      lasttime = time.time();
      display.render();
