# the light board class and supporting classes
import time;
import serial;
import fileinput;
import sys;
import StringIO;

SYNCVALUE = 0x69;

# This class is internal. No reason for the outside world to ever know about it.
class CheckSum:
   def __init__(this):
      this.chksum = 0;
      
   def Next(self, value):
      self.chksum = (((self.chksum & 0x7F) << 1) | ((self.chksum & 0x80) >> 7)) & 0xFF;
      self.chksum += value;
      if (self.chksum >= 256):
         self.chksum -= 256;
      
#This class actually does the work of staying connected to an arduino on an individual serial port.
# Note, since this is bound to the SerialID, and those aren't guarunteed to be persistent, 
#we could end up with differen LBTs tracking the same actual Arduino over the lifecycle of the program
class LightBoardTracker:
   def __init__(this):
      this.guid = 0;
      this.working = LightBoardState();
      this.isOpen = False;
      this.portindex = -1;
      this.lastgood = None;
      this.ser = None;
      this.triedopen = time.time() - 5;
      this.__timetried = time.time() - 2;
      this.lid = -1;

   def setLid(this, lid):
      this.lid = lid;
      
   def triednow(this):
      this.__timetried = time.time();
      
   def timesincetried(this):
      return  time.time() - this.__timetried;
   
   def isOpen(this):
      return this.isOpen;
   
   
   def openSerial(this, serialID):
      # Note:  Calling this method will pick up the default serial speed (currently configured as 76800 baud)
      #  This is the method that the cube calls to open the serial ports.  
      openSerialSpeed(this, serialID, 76800);
   
   def openSerialSpeed(this, serialID, baud):
      if (time.time() - this.triedopen < 5):
         return;
      if (this.isOpen):
         if (hasattr(this.ser, "_isopen")):
            if (this.ser._isopen and this.portindex == serialID):
               return;
      try:
         this.triedopen = time.time();
         #print "Asking to open "
         #print serialID
         #this.ser = serial.Serial(serialID, 9600, EIGHTBITS, PARITY_NONE, STOPBITS_TWO, None, xonxoff=0, rtscts=0, None, None, None);
         this.ser = serial.Serial(serialID, baud, 8, 'N', 1, None, 0, 0, None, None, None);
         # Use this on a MAC (apparently)
				 #this.ser = serial.Serial('/dev/tty.usbserial-A6008iGf', 9600, 8, 'N', 1, None, 0, 0, None, None, None);
         
         print "Successfully opened serialID:"
         print serialID;
         
         #print "past that"
         this.isOpen = True;
      except (KeyboardInterrupt, SystemExit):
         raise
      except:
         print "Unexpected error:", sys.exc_info()[0]
         this.isOpen = False;
         this.ser = None;
      finally:
         0;
         
   def close(this):
      this.portindex = -1;
      this.isOpen = False;
      if (this.ser != None):
         this.ser.close();      
      
   def read(this):
      try:
         ser = this.ser;
         if (ser != None and ser._isOpen):
            while (ser.inWaiting() > 0):
               this.working.read(ser);
               if (this.working.complete):
                  if (this.working.valid):
                     this.lastgood = this.working;
                     #if (ser.inWaiting() > 18):
                     #print "Flushing";
                     #ser.flushInput();
                     #this.working = LightBoardState();
                     #return;
                  else:
                     print "Invalid message deserialized";
                     print this.lid;
                  this.working = LightBoardState();
      except (KeyboardInterrupt, SystemExit):
         raise
      except:
         try:
            print "Closing serial port due to exception during read";
            ser.close();
         finally:
            this.ser = None;
            this.isOpen = False;
            this.portindex = -1;
      finally:
         return;
               
   def timesince(this):
      working = getattr(this, "working");
      return working.timesince();

  
#  Fields:
#     guid -- The identifier for the board. These are 0 based, but logically, '1' corresponds to the board marked 'A' 
#     powermodule1 -- The current output from pm 1
#     powermodule2 -- The current output from pm 2
#     pixels -- A list of lists.  Format is [ [ p0.r, p0.g, p0.b], ... , [p4.r, p4.g, p4.b]]
#     valid -- boolean set to true iff this checksums correctly
#     complete -- boolean set to true iff we have read the right number of bytes off the wire to complete this 
#     __timestarted -- the time we began decoding this message
class LightBoardState:
   def __init__(this):
      this.guid = 0;
      this.powermodule1 = 0;
      this.powermodule2 = 0;       
      this.pixels = [ [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0]];
      this.__readstate = 0;
      this.__reading = False;
      this.valid = False;
      this.complete = False;
      this.__timestarted = time.time();
      
   def timesince(this):
      return time.time() - this.__timestarted;

   def add(this, b):
      if (not this.__reading):
         if (ord(b) == SYNCVALUE):
            this.__reading = True;
            this.__check = CheckSum();
            this.__check.Next(ord(b));
            this.__timestarted = time.time();
            return;
         else: 
            return;
      if (this.__readstate == 19):
         this.complete = True;
         if (this.__check.chksum == ord(b)):
            this.valid = True;
            this.__timeFinished = time.time();
         else:
            print("Checksum failed:  Looking for {0}, found {1}".format(this.__check.chksum, ord(b)));
         return;
      if (this.__readstate == 0):
         this.guid = ord(b);
      if (this.__readstate == 1):
         this.powermodule1 = b;
      if (this.__readstate == 2):
         this.powermodule2 = b;
      if (this.__readstate == 3):
         this.latency = b;
      if (this.__readstate >= 4 and this.__readstate < 19):
         iPixel = int((this.__readstate - 4) / 3);
         iColor = int((this.__readstate - 4) % 3);
         this.pixels[iPixel][iColor] = b;
      this.__check.Next(ord(b));
      this.__readstate = this.__readstate + 1;
         
   def read(this, ser):
      if this.complete:
         return;
      inWaiting = ser.inWaiting();
      bytesWaiting = ser.read(inWaiting);
      for b in bytesWaiting:
         if this.complete:
            return;
         this.add(b);
         
      #while((ser.inWaiting() > 0) and (this.complete == False)):
      #   this.add(ser.read());

#  This is used to create command messages to the Arduinos. 
#  The proper usage is always to call this via either
#    createFromQuantizedPixelList
#      or
#    createFromFPPixelList
class Message:
   def beginmessage(self):
      self.sio = StringIO.StringIO();
      self.sio.write(chr(SYNCVALUE));
      #self.m = "" + chr(SYNCVALUE);
      self.__check = CheckSum();
      self.__check.Next(SYNCVALUE);
      
   def endmessage(self):
      #self.m += chr(self.__check.chksum);
      self.sio.write(chr(self.__check.chksum));
   def addbyte(self,value):
      self.sio.write(chr(value));
      #self.m += chr(value);
      self.__check.Next(value);
      
   def createFromQuantizedPixelList(self, lrp, list):
      self.beginmessage();
      self.addbyte(lrp);
      for pixel in list:
         for b in pixel:
            self.addbyte(b);
      self.endmessage();
      return self.sio.getvalue()
   
   def createFromFPPixelList(self, lrp, list):
      self.beginmessage();
      self.addbyte(lrp);
      for pixel in list:
         for fp in list[pixel]:
            b = int(fp * 255);
            self.addbyte(b);
      self.endmessage();
      return self.sio.getvalue()

# This is an internal class supporting LightMapping.  
#  There is no reason for clients of this file to ever use this class
class BoardMap:
   def __init__(self):
      self.pixels = [];
      self.offsets = []; # These are mapped to physical PixelIDs
      self.lbt = None;
      self.id = None;
      for x in range(5):
         self.pixels.append(-1);
         self.offsets.append([1,1,1]);

#fields:  
#    pixelMap --> A hashmap which goes from the logicalPixelID to the Input line that created it (And hence, the boardID, and physical pixelID)
#                   Can be out of date as it is not updated when pixels are swapped, etc.
#    boardMap --> A hashmap of boardMaps that goes from boardID, to a BoardMap object, containing:
#         a LightBoardTracker (if there is one tracking this item)
#         an ID, 
#         a list of 5 pixelIDs
class LightMapping:
   def initMapping(this, file):
      this.pixels = [];
      for x in range(54):
         this.pixels.append([128,0,0]);
      this.pixelMap = {};
      this.boardMap = {};
      for line in fileinput.input(file):
         l = eval(line);
         logicalPixelID = l[0];
         boardID        = l[1];
         boardPixelID   = l[2];
         physPixelOffset = l[3];
         if (not this.boardMap.__contains__(boardID)):
            this.boardMap[boardID] = BoardMap();            
         this.pixelMap[logicalPixelID] = list(l);
         this.boardMap[boardID].pixels[boardPixelID] = logicalPixelID;
         this.boardMap[boardID].offsets[boardPixelID] = physPixelOffset 
   
   def addBoard(this, lbt):
      id = lbt.lastgood.guid;
      bm = this.boardMap[id];
      bm.lbt = lbt;
      
   def dropBoard(this, lbt):
      this.boardMap[lbt.lastgood.guid].lbt = None;
      
   def tracking(this, lbt):
      if (lbt.lastgood != None and this.boardMap[lbt.lastgood.guid].lbt != None):
         return True;
      return False;

   # we need to update the in-memory fields
   #    pixelMap
   #    boardMap
   def switchPixels(this, iPixelOne, iPixelTwo):
      # Update the pixelMap
      #  Note, these are references, so updating them updates the original list as well.
	  # Correctly does not update color offsets as those are physical pixel ID dependent
      pixelOne = this.pixelMap[iPixelOne]
      pixelTwo = this.pixelMap[iPixelTwo]
      
      #Note, since these will hold int's, they are value, not reference, and so will persist
      p1_ID    = pixelOne[0];
      p1_BOARD = pixelOne[1];
      p1_PIXEL = pixelOne[2];
      
      p2_ID    = pixelTwo[0];
      p2_BOARD = pixelTwo[1];
      p2_PIXEL = pixelTwo[2];
      
      pixelOne[0] = p2_ID;
      pixelTwo[0] = p1_ID;
      
      # Update the pixelMap
      this.pixelMap[iPixelOne] = pixelTwo;
      this.pixelMap[iPixelTwo] = pixelOne;

            
      # Update the boardMap
      this.boardMap[p1_BOARD].pixels[p1_PIXEL] = p2_ID;
      this.boardMap[p2_BOARD].pixels[p2_PIXEL] = p1_ID;
      
   def dumpMapping(self, fileName):
      file = open(fileName, 'w');
      for ID in self.pixels:
         file.writelines([self.pixels[ID].__str__()]);
      file.flush();
      file.close();

   # Don't want to modify dumpMapping, don't know what uses it
   # This saves a complete Mapping that can be loaded with initMapping
   def saveMapping(self, file):
      pixelMap = []
      for i, board in self.boardMap.items():
          boardID = i
          for j, pixel in enumerate(board.pixels):
              boardPixelID = j
              if (pixel == -1 ):
                  # this pixel doesn't actually exist, the last open lightboard slot on the last arduino
                  continue
              logicalPixelID = pixel
              physPixelOffset = tuple(board.offsets[j])
              pixelMap.append( (logicalPixelID, boardID, boardPixelID, physPixelOffset  ) )
              
      pixelMap.sort(key=lambda x:x[0])
      output = open(file, 'w');
      for line in pixelMap:
          output.write("( %s, %s, %s, %s )\n" % line)
      output.close();

   
   # Called when pixels will be remapped from the admin panel
   # Turns off all pixels, walks through and flashes one pixel at a time
   def adminRemap(self):
       pass

   
   #Note:  Frames is a list of lists.  Format is:
   # [ [ lrpDurationInLrpCycles, [P_0.b, P_0.g, P_0.r], [P_1.b, P_1.g, P_1.r], ... , [P_51.b, P_51.g, P_51.r] ],
   #   [ lrpDurationInLrpCycles, [P_0.b, P_0.g, P_0.r], [P_1.b, P_1.g, P_1.r], ... , [P_51.b, P_51.g, P_51.r] ],
   #   ....
   # ]
   # lrpDurations are in bytes, 1 lrpDuration == 4 ms
   # Pixel Values are quantized values from 0 - 255.
   def renderFrames(this, frames, resync):
      self = this
      start = time.time();
      
      #if len(resync) > 0:
      #   frames.insert( 0, [50, resync] );

      for bmID in iter(this.boardMap):
         message = "";
         boardmap = this.boardMap[bmID];
         if (boardmap == None or boardmap.lbt == None or boardmap.lbt.ser == None):
            continue;
         
         now = time.time();
         startFrame = start;
         lag = now - start;
         m = Message();
         
         for frame in frames:
            frameClock = time.clock()
            lrp = frame[0];
            lrpLag = 0;
            pixels = frame[1];            
            endFrame = startFrame + (lrp * .004);

            if (now < endFrame or True):
               if (True or len(resync) > 0):
                  if (now >= startFrame):
                     lag = now - startFrame;
                     lrpLag = int(lag * 1000 / 4);
                  if (now >= endFrame):
                     lrpLag = lrp;
               pv = {};
               # Iterate over each board,
               # Look up the pixels tied to that board
               #  ? Update them if necessary
               #  Send a message to the board.
               p = [0,0,0,0,0];
               
               for x in range(5):
                  p[x] = boardmap.pixels[x];
                  pv[x] = [ i*j for i, j in zip(pixels[p[x]],boardmap.offsets[x]) ]
                  
               #print("LRP : {0}".format(lrp - lrpLag));
               message = message + m.createFromFPPixelList(lrp - lrpLag, pv);

            # update our loop state
            lrpLag = 0;
            startFrame = endFrame;

         if (message != ""):
            #print "Sending message for board: {0}, length: {1}".format(bmID, message.__len__());
            try:
               preNetClock = time.clock()
               boardmap.lbt.ser.write(message);
               postNetClock = time.clock()
               #print "  MT: " + str( preNetClock - frameClock ) + " NT: " + str( postNetClock - preNetClock ) + " FC: " + str( len( frames ) )
            except (KeyboardInterrupt, SystemExit):
               raise
            except:
               print "Managing exception on board {0}".format(bmID);
            finally:
               0
      

         
         
