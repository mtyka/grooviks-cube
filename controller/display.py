import lightboard
import time;
import platform
from logme import * 

from glog import GLog;
from groovikutils import dev_mode

# parameters
#    cTrackers -- The total search space for serial ports.  We'll start w/ 0, and go to this number in our scan.
#    input filename -- This file will contain the mapping which defines the logical pixel to board/physical pixel relationship

# actions
#    init
#    acquire
#    maintenance
#       read buffers
#       clear MIA boards
#       reacquisition (if necessary)
#    render

# properties
#    pixels

class Display:
   def __init__(self, cTrackers, fileName):
      self.logInterval = 60;
      self.lastLogged = 0;
      self.logger = GLog("power.log");
      self.dirty = True;
      logme( "Display Init" )
      self.trackers = {}; # a hash to hold the lightBoardTrackers;
      self.cTrackers = cTrackers;
      self.inputFileName = fileName;
      for j in range(cTrackers):
         i = cTrackers - j - 1;
         logme( "First try for light board:", i )
         self.trackers[i] = lightboard.LightBoardTracker();
         if (platform.system() == 'Darwin' ):
             logme( "Darwin System" )
             self.trackers[i].openSerial('/dev/tty.usbserial-A6008iGf');
         else:
             logme( "Linux System" )
             self.trackers[i].openSerial(i);
         self.trackers[i].setLid(i);
       
      # 5 second delay to let the arduino boards stabilize
      time.sleep(2);
      
      # read in the file mapping facets to arduino IDs
      self.lm = lightboard.LightMapping();
      self.lm.initMapping(fileName);
      logme( "Display init end" )
   
   def print_trackers_to_log(self):
      for i in range(self.cTrackers):
         if self.trackers[i].ser != None:
            logme( "Tracker[%d]: "%i + self.trackers[i].str() );
      

   def loop(self):
      if dev_mode:
          return
      log = False;
      now = time.time();
      if ((now - self.lastLogged) > self.logInterval):
         self.lastLogged = now;
         log = True;
         logLines = [];

      disconnection_at_the_start = False
      if log or self.lm.countTracked() < 11:
        disconnection_at_the_start = True
        logme( "Start of loop: Trackers: %d ------------------------------------------------------------------------------ "%self.cTrackers )
        logme( "self.lm.countTracked(): %d"%(self.lm.countTracked()))
        self.print_trackers_to_log()

      #  Here we need to:
      #    Handle light arduinos

      for i in range(self.cTrackers):
         tracker = self.trackers[i];
         #         Decode all waiting pong messages
         tracker.read();      
         if (tracker.lastgood != None and log):
            logmessage  = str(timestamp()) + " ID: {0:c}, PW1: {1:d}, PW2: {2:d}\n".format((tracker.lastgood.guid + ord('a') - 1), ord(tracker.lastgood.powermodule1), ord(tracker.lastgood.powermodule2));
            logLines.append( logmessage )

         #         Make sure "last" state matches our expected state
         # if we haven't heard from one in a "long time", then set it to faulted.
         if (tracker.timesince() > 2 and tracker.timesincetried() > 2):
            # if we had been tracking this, and it had been mapped, and this is the first time we've failed to track it,
            # unmap it, note that we've done so.
            if (tracker.lastgood != None):
               logme( "Dropping board %d because of non-responsiveness" % tracker.guid )
               self.lm.dropBoard(tracker);
               tracker.lastgood = None;

            # only try to reconnect if we are not actively tracking all arduinos
            if (self.lm.countTracked() < 11):
               #logme( "Reconnecting to lightboard %d" % i )
               
               #tracker.close();
               tracker.openSerial(i);
               tracker.triednow();
            
         if (tracker.lastgood != None and tracker.guid != tracker.lastgood.guid):
            #drop the old board from the mapping
            if (tracker.guid != 0):
               self.lm.dropBoard(tracker);
            #update the guid on the tracker
            tracker.guid = tracker.lastgood.guid;
         if (tracker.lastgood != None and not self.lm.tracking(tracker)):
            #update our mapping as appropriate
            self.lm.addBoard(tracker);
      
      
      if disconnection_at_the_start:
        logme( "End of loop: Trackers: %d ------------------------------------------------------------------------------ "%self.cTrackers )
        logme( "self.lm.countTracked(): %d"%(self.lm.countTracked()))
        self.print_trackers_to_log()

      if log:
         self.logger.logLines(logLines);
         log = False;

   #Note:  Frames is a list of lists.  Format is:
   # [ [ lrpDurationInLrpCycles, [P_0.b, P_0.g, P_0.r], [P_1.b, P_1.g, P_1.r], ... , [P_51.b, P_51.g, P_51.r] ],
   #   [ lrpDurationInLrpCycles, [P_0.b, P_0.g, P_0.r], [P_1.b, P_1.g, P_1.r], ... , [P_51.b, P_51.g, P_51.r] ],
   #   ....
   # ]
   # lrpDurations are in bytes, 1 lrpDuration == 4 ms
   # Pixel Values are quantized values from 0 - 255.
   def renderFrames(self, frames, resync):
      self.lm.renderFrames(frames, resync);
      
   def render(self):
      if (self.dirty):
         frame = [];
         frame.append(100);
         frame.append([]);
         for i in range (54):
            frame[1].append(self.lm.pixels[i]);
         self.lm.render();
         self.dirty = False;
      
   def setPixel(self, iPixel, pixelValue):
      if (pixelValue[0] != self.lm.pixels[iPixel][0] or pixelValue[1] != self.lm.pixels[iPixel][1] or pixelValue[2] != self.lm.pixels[iPixel][2]):
         self.lm.pixels[iPixel] = pixelValue;
         self.dirty = True;
         
   def getPixels(self, iPixel):
      self.lm.pixels[iPixel];
      
   def close(self):
      for bmID in iter(self.lm.boardMap):
         boardmap = self.lm.boardMap[bmID];
         if (boardmap != None and boardmap.lbt != None and boardmap.lbt.ser != None):
            boardmap.lbt.ser.close();
      

      
