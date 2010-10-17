#imports 

#import standard libraries
import fileinput
import time
import socket
import sys
import traceback

#import uistation;
from uistation import UiStation
from UIManager import UIManager;
from glog import GLog;
from GScript import GScriptLibrary;

#import extensions
import serial

#import our own binaries
import groovik
import lightboard
import display

from GScript import GScript
from uistation import UiStation

import sys;
log = GLog("fatal.log");

ilogcnt = 0;
locked = False;

try:
   
   plat = sys.platform.lower()
   count = 25;
   if   plat[:5] == 'linux':
      count = 11;
   
   ui = UIManager();
   display = display.Display(count, "input2.py");
   
   # Give the arduinos time to go through their reset sequence.  5 seconds is overkill, but... better safe then sorry.
   time.sleep(5);
       
   lasttime = time.time();
   
   preStartupLibrary = GScriptLibrary();
   preStartupLibrary.Load("prestartup.library");
   
   startupLibrary = GScriptLibrary();
   startupLibrary.Load("startup.library");
   
   moveLogger = GLog("moves.log");
   moveLogger.logLine("[ \"reset\" ]");
   
   grooviksCube = groovik.GrooviksCube(moveLogger);
   grooviksCube.SetStartTime( time.time() );   
   
   #preStartupLibrary.ForceQueueByRandom(grooviksCube);
   preStartupLibrary.ForceQueueByID("checkerboard", grooviksCube);
   
   #and now randomize...   
   cFrames = 0
   timeStart = time.time()
   

   sim_time = time.time();
   wall_time = time.time();
   
   #grooviksCube.QueueVictory();
   startup = GScript();
   startup.CreateRandom(30, .5);
   startup.ForceQueue(grooviksCube);

   while(True):
      now = time.time();
      if (now - timeStart > 2):
         #print "Framerate"
         #print cFrames / (now - timeStart)
         cFrames = 0
         timeStart = now
         
      #sample the input
      results = ui.update()
      if results:
         rotations = [];
         for result in results:
            command = result;
            # if this is a rotation...
            if (command < 18):
               rot = command / 2
               reverse = command % 2
               rotations.append( [rot, reverse] )
         print "queuing rotation";
         if ( grooviksCube.QueueRotation( rotations ) ):
            ui.broadcast('L');
            locked = True;
   
      #handle any display management 
      display.loop();
      
      wall_time = time.time();
      while (wall_time < (sim_time - groovik.TIMESTEP / 3)):
         ilogcnt += 1;
         display.loop()
         
         wall_time = time.time()
               
      #print "Entering update";
      keyframes, resync = grooviksCube.Update( sim_time );
      display.renderFrames( keyframes, resync );
      #print "Exiting render";
      cFrames += 1;
      
      if (grooviksCube.IsIdle()) and locked:
         locked = False;
         ui.broadcast('U');
         
      sim_time += groovik.TIMESTEP;
      lasttime = time.time()
except Exception, err:
   log.logLines([str(time.time()), str(traceback.format_exc())]);
   
