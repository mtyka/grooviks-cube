#
# Groovik state object
#
# Groovik's cube has 54 colors, arranged (at the moment) in this fashion:
#  x = 1        x = -1         y = 1         y = -1        z = 1       z = -1
# Z           Z              Z             Z             Y            Y
# ^           ^              ^             ^             ^            ^
# |6 7 8      |15 16 17      |24 25 26     |33 34 35     |42 43 44    |51 52 53
# |3 4 5      |12 13 14      |21 22 23     |30 31 32     |39 40 41    |48 49 50
# |0 1 2      |9  10 11      |18 19 20     |27 28 29     |36 37 38    |45 46 47
#  ------> Y   --------> -Y   -------> -X   --------> X   -------->X   --------> -X

import sys
import math
import random
import copy
import time 

from GScript import GScriptLibrary
from GScript import GScript
from event_manager import CubeEventManager
from groovikutils import *
from statedelay import StateDelay
from statefade import StateFade
from stateidle import StateIdle
from stateidlepulse import StateIdlePulse
from staterotation import StateRotation
from statespiralfade import StateSpiralFade
from statestrobe import StateStrobe
from modenormal import ModeNormal
from modecalibration import ModeCalibration
from modelightboardconfiguration import ModeLightBoardConfiguration
from modescreensaver import ModeScreenSaver
from groovikconfig import *

   
   
#-------------------------------------------------------------------------------
# This class represents the cube itself and its queued commands
#-------------------------------------------------------------------------------
class GrooviksCube:         
   #-----------------------------------------------------------------------------
   # The following methods are used to query cube simulation state:
   # * What 'cube state' is currently acting on the cube?
   # * What 'game mode' are we in?
   # * What is the current output colors (GetCorrectedColors): these have been color corrected + remapped for the lightboards
   # * What is the set of unique (non-corrected) colors on the cube ('FaceColors'): this can be different than 6 colors
   # * Has any cube states been queued and is waiting to become active?
   #-----------------------------------------------------------------------------
   def IsCurrentlyRotating( self ):
      return self.__currentCubeState == CubeState.ROTATING
   
   def IsIdle( self ):
      return self.__currentCubeState == CubeState.IDLE
   
   def   GetCurrentState( self ):
      return self.__currentCubeState
   
   def GetCurrentMode( self ):
      return self.__currentCubeMode
   
   def GetCorrectedColors( self ):
      return self.__RemapOutputs( self.__colors )
   
   def GetFaceColors( self ):
      return self.__faceColors   
   
   def GetFaceColorIndicies( self ):
      return self.__initialColorIndices;
   
   def HasQueuedStates(self): 
      return ( len( self.__queuedStates ) > 1 )
   
   #-----------------------------------------------------------------------------
   # This method is how input events are posted to the simulation
   # cubeInputType is a member of the CubeInput enum. Params is different
   # depending on which input type is used, see the CubeInput enum docs
   #-----------------------------------------------------------------------------   
   def HandleInput( self, cubeInputType, params ):
      # always handle mode switch ourselves. Otherwise, let the current mode deal.
      self.LogEvent( "Input : " + str(cubeInputType) + ", " + str( params ) );
      if ( cubeInputType == CubeInput.SWITCH_MODE ):
         self.QueueModeChange( params )
      else:
         self.__currentMode.HandleInput( self, self.display, cubeInputType, params )
   
   #-----------------------------------------------------------------------------
   # This method will queue a game mode change. mode is member of the CubeMode enum.
   #-----------------------------------------------------------------------------
   def QueueModeChange( self, mode ):
      if ( self.__CanQueueState( CubeState.SWITCH_MODE ) ):
         # Always fade out before switching modes
         self.__AppendState( [ CubeState.FADE, 0.5, False, [0.0, 0.0, 0.0] ] )
         self.__AppendState( [ CubeState.SWITCH_MODE, mode ] )
      
      
   #-----------------------------------------------------------------------------   
   # Methods related to queueing cube state changes.
   # Note that these will all trigger calls to the current game mode's CanQueueState method
   # You can also look at these to see the format of the state change objects
   # used to describe static state lists found in scripts such as the victory script
   #-----------------------------------------------------------------------------
   
   # This state will pulse toward black and back to the current color over the specified duration (a float)
   def QueueIdlePulse( self, duration ):
      if ( self.__CanQueueState( CubeState.IDLEPULSE ) ):
         self.__AppendState( [ CubeState.IDLEPULSE, duration ] )
      
   # This state will fade the cube to the specified colors
   # duration is a float indicating the time of the fade
   # fadeInHSL is a bool, indicating whether to do color lerping in RGB or HSL space
   # faceColorIndices can take a number of optional forms:
   #    * None: causes the cube to fade to the initial state specified by the current game mode
   #    * [ r g b ] (an array of 3 floats): Causes the cube to fade to the specified (r,g,b) color
   #    * [ 54 integers ] (indices into the cube's unique 'faceColor' list): Causes the cube pixels
   #      to fade to the specified pattern. Specifying an index of -1 results in a black pixel.
   def QueueFade( self, duration, fadeInHSL, faceColorIndices ):
      if ( self.__CanQueueState( CubeState.FADE ) ):
         self.__AppendState( [ CubeState.FADE, duration, fadeInHSL, faceColorIndices ] )

   # This state will perform a 'spiral' fade on the cube to the specified colors
   # duration is a float indicating the time of the fade
   # axis is an integer 0-2 indicating the axis around which the spiral should occur
   # fadeInHSL is a bool, indicating whether to do color lerping in RGB or HSL space
   # faceColorIndices can take a number of optional forms:
   #    * None: causes the cube to fade to the initial state specified by the current game mode
   #    * [ r g b ] (an array of 3 floats): Causes the cube to fade to the specified (r,g,b) color
   #    * [ 54 integers ] (indices into the cube's unique 'faceColor' list): Causes the cube pixels
   #      to fade to the specified pattern. Specifying an index of -1 results in a black pixel.
   def QueueSpiralFade( self, duration, axis, fadeInHSL, faceColorIndices ):
      if ( self.__CanQueueState( CubeState.SPIRALFADE ) ):
         self.__AppendState( [ CubeState.SPIRALFADE, duration, axis, fadeInHSL, faceColorIndices ] )
   
   # This state will strobe the cube back + forth between the specified colors and the current colors
   # duration is a float indicating the total time over which the cube should strobe on + off
   # strobeDuration is a float indicating the time of a single strobe. Needs to be <= duration. 
   #    If they are equal, the cube will only strobe once.
   # fadeInHSL is a bool, indicating whether to do color lerping in RGB or HSL space
   # faceColorIndices can take a number of optional forms:
   #    * [ r g b ] (an array of 3 floats): Causes the cube to strobe to the specified (r,g,b) color
   #    * [ 54 integers ] (indices into the cube's unique 'faceColor' list): Causes the cube pixels
   #      to strobe to the specified pattern. Specifying an index of -1 results in a black pixel.
   def QueueStrobe( self, duration, strobeDuration, fadeInHSL, faceColorIndices ):
      if ( self.__CanQueueState( CubeState.STROBE ) ):
         self.__AppendState( [ CubeState.STROBE, duration, strobeDuration, fadeInHSL, faceColorIndices ] )
         
   # This state will make the cube inert for the specified time.
   # duration is a float indicating the total time over which the cube should strobe on + off
   def QueueDelay( self, duration ):
      if ( self.__CanQueueState( CubeState.DELAY ) ):
         self.__AppendState( [ CubeState.DELAY, duration ] )
         
   # This will queue multiple rotations. The rotations parameter is of the form
   # [ [ <rotation type>, <clockwise> ], [ <rotation type>, <clockwise> ], ... ]
   # rotation type is an integer from 0 to 8. 
   # 0-2 represent rotations around the X axis of the 1st, 2nd, and 3rd rows, respectively.
   # 3-5 represent rotations around the Y axis of the 1st, 2nd, and 3rd rows, respectively.
   # 6-8 represent rotations around the Z axis of the 1st, 2nd, and 3rd rows, respectively.
   # clockwise is a bool indicating whether the rotation should be clockwise
   def QueueRotation( self, rotations ):
      # Disallow illegal rotations
      actualRotations = []
      validRotations = [ True, True, True, True, True, True, True, True, True ]
      for rotation in rotations:
         index = rotation[0]
         if ( not validRotations[ index ] ):
            continue
         actualRotations.append( rotation )
         validRotations[ index ] = False
         family = int( index / 3 ) * 3
         for i in range( 9 ):
            if ( i >= family and i < family + 3 ):
               continue
            validRotations[ i ] = False
            
      if ( self.__CanQueueState( CubeState.ROTATING ) ):    
         self.__AppendState( [ CubeState.ROTATING, actualRotations, -1, True ] )
         # relies on one axis at a time being rotated..
         rows = []
         dirs = []
         for r in rotations:
            rows.append(r[0]%3)
            dirs.append(r[1])
         self.__event_manager.rotate(r[0]/3, rows, dirs, self.__rotationState.rotationTime) 
            
      else:
         for r in rotations:
            self.__event_manager.invalid_move(r[0]/6)
      return True
      
   #-----------------------------------------------------------------------------   
   # This will queue a pre-authored effect described in the effects.library file.
   # That file contains lines of the form [ CubeState, <other params> ]
   # Look at the other state queuing methods to see the param formats
   #-----------------------------------------------------------------------------
   def QueueEffect( self, effectName ):
      self.__ClearRotationQueue()
      self.LogEvent( "Effect : " + effectName );
      groovikConfig.effectsLibrary.ForceQueueByID( effectName, self );
      if ( effectName == "victory0" ):
         self.__event_manager.reward(15) #15 is the magic victory number
   
   #-----------------------------------------------------------------------------
   # This immediately resets the cube to the initial state of the current mode,
   # clears all queued cube states, and resets the current cube state to idle.
   #-----------------------------------------------------------------------------
   def ResetColors( self ):
      # reset colors
      self.LogEvent( "Reset" );
      self.__colors = []
      for i in range( len(self.__initialColorIndices) ):
         if ( self.__initialColorIndices[i] >= 0 ):
            self.__colors.append( self.__faceColors[ self.__initialColorIndices[i] ][:] )
         else:
            self.__colors.append( [0.0, 0.0, 0.0] )
      self.__ClearRotationQueue( )


   def Randomize( self, depth ):
      self.__normalMode.Randomize(self, depth)

   #-----------------------------------------------------------------------------
   # This is the main simulation method of the cube. Pass in the time to simulate to
   #-----------------------------------------------------------------------------
   def Update( self, currentTime ):
      self.__ProcessQueuedStates( currentTime )
      
      if ( self.__currentCubeState != CubeState.IDLE ):
         lastTime = self.__lastSimTime
         resync = []
      else:
         lastTime = currentTime
         resync = copy.deepcopy( self.__colors )

      colorKeyframes = []
      simStartClock = time.clock()
      rotationStep = 0;

      while True:
         # Do simulation
         output = self.__currentState.Update( currentTime )
         
         # Interpret return values
         stateFinished = output.pop()
         simTime = output.pop()
                  
         # time is in cycles; each cycle is 4ms (see lightboard.py)
         lrpCycles = int( (( simTime - lastTime ) / 0.004) + .5 ) 
         if ( lrpCycles > 255 ):
            lrpCycles = 255
         colorKeyframes.append( [ lrpCycles, output[0] ] )
         
         # tracks the current rotation step we're on, if we're rotating
         if len(output) > 1:
             rotationStep = output[1]         
 
         lastTime = simTime
         
         # provide an opportunity for code to supply cube states
         self.__currentMode.SelectNewState( self, currentTime, output[0], stateFinished )
      
         # The idle state never says its finished; it's done if we have other states
         queueLength = len( self.__queuedStates )
         if ( ( self.__currentCubeState == CubeState.IDLE ) and ( queueLength > 0 ) ):
            stateFinished = True
            
         if ( stateFinished is True ):
            # Add one last keyframe to take us through to currentTime
            #if ( simTime != currentTime ):
            #  lrpCycles = int( (( currentTime - simTime ) / 0.004) +.5 ) 
            #  if ( lrpCycles > 255 ):
            #     lrpCycles = 255
            #  colorKeyframes.append( [ lrpCycles, output[0] ] )
            
            self.__currentCubeState = CubeState.UNKNOWN
            break
         
         # Stop looping when we hit the current time
         if ( simTime == currentTime ):
            break
      
      simEndClock = time.clock()
      frameClockDuration = simEndClock - self.__lastSimClock
      self.__lastSimClock = simEndClock
      diffTime = currentTime - self.__lastSimTime; 
      self.__lastSimTime = currentTime
      self.__colors = copy.deepcopy( colorKeyframes[ len( colorKeyframes ) - 1 ][1] )
      duration = 0;
      for f in colorKeyframes:
         duration += f[0]
         # Perform lightboard remapping + color correction
         f[1] = self.__RemapOutputs( f[1] )
      resync = self.__RemapOutputs( resync )
      #print "CT: " + str( currentTime ) + "LT: " + str( lastTime ) + "FT: " + str( frameClockDuration ) + " ST: " + str( simEndClock - simStartClock ) + " NK: " + str( len(colorKeyframes) ) + " resync: " +str(len(resync)) + " duration " + str(duration) + ", " + str(int(diffTime * 250));
      return colorKeyframes, resync, rotationStep

   #-----------------------------------------------------------------------------
   # Methods related to initialization of the cube simulation
   #-----------------------------------------------------------------------------
   def __init__(self, logger, display):
      self.__queuedStates = [ ]
      self.display = display

      # create all states
      self.__idleState = StateIdle()
      self.__idlePulseState = StateIdlePulse()
      self.__rotationState = StateRotation()
      self.__strobeState = StateStrobe()
      self.__fadeState = StateFade()
      self.__spiralFadeState = StateSpiralFade()
      self.__delayState = StateDelay()
      
      # create all modes
      self.__normalMode = ModeNormal()
      self.__calibrationMode = ModeCalibration()
      self.__lightBoardConfiguration = ModeLightBoardConfiguration()
      self.__screensaver = ModeScreenSaver()
      
      self.__currentCubeState = CubeState.UNKNOWN
      self.__currentCubeMode = CubeMode.UNKNOWN
      self.__event_manager = CubeEventManager(0)
      self.__logger = logger
      
      # Start all colors black; we always fade into our mode switches.
      self.__colors = []
      self.__faceColors = []
      self.__initialColorIndices = []
      for f in range( 0, 6 ):
         self.__faceColors.append( [0.0, 0.0, 0.0] )
      for i in range( 0, 54 ):
         self.__colors.append( [0.0, 0.0, 0.0 ] )
         self.__initialColorIndices.append( -1 )
         
      # Skip 
      self.__AppendState( [ CubeState.SWITCH_MODE, CubeMode.SCREENSAVER ] )
      
   def SetStartTime( self, currentTime ):
      self.__appStartTime = currentTime
      self.__startTime = currentTime
      self.__lastSimTime = currentTime
      self.__lastSimClock = time.clock()
   
   # This method is designed exclusively for the GScript method of authoring pre-scripted transitions
   # and shouldn't be called outside of that
   def ForceQueueCubeState( self, params ):
      # upconvert old-style files
      if ( params[0] == CubeState.ROTATING_OLDSTYLE ):
         if ( len(params) == 3 ):
            params = [ CubeState.ROTATING, self.__ConvertRotationParams( params ) ]
         elif ( len(params) == 4 ): 
            params = [ CubeState.ROTATING, self.__ConvertRotationParams( params ), params[ 3 ] ]
         else:
            params = [ CubeState.ROTATING, self.__ConvertRotationParams( params ), params[ 3 ], params[ 4 ] ]
      self.__AppendState( copy.deepcopy( params ) )

   
   #-----------------------------------------------------------------------------
   # Implementation details below here
   #-----------------------------------------------------------------------------   
   def __CanQueueState( self, state ):
      # Illegal to queue states during a transition
      if ( self.__currentCubeState != CubeState.IDLE and self.__currentCubeState != CubeState.UNKNOWN ):
         return False
      
      return self.__currentMode.CanQueueState( self, state )
      
   def __ConvertRotationParams( self, params ):
       return [ [ params[1], params[2] ] ]
      
   def __ProcessQueuedStates( self, currentTime ):
      if ( self.__currentCubeState != CubeState.UNKNOWN ):
         return

      # If the queue is empty, and we're not in an idle state, force an idle state
      # by inserting an idle command into the queue. We bypass __AppendState
      # because it's checking for IDLE states getting queued, which is illegal.
      if ( len( self.__queuedStates ) == 0 ):
         if ( self.__currentCubeState == CubeState.IDLE ):
            return
         self.__queuedStates.append( [ CubeState.IDLE ] );

      self.__currentCubeState = self.__queuedStates[0].pop( 0 )
      
      # Mode switches are handled specially. This clears the queue
      # and the mode is responsible for setting up any initial state, 
      if ( self.__currentCubeState == CubeState.SWITCH_MODE ):
         params = self.__queuedStates[0]
         self.__ClearRotationQueue()
         self.__SwitchMode( params )
         self.__startTime = self.__lastSimTime = currentTime
         self.__currentCubeState = self.__queuedStates[0].pop( 0 )
         
      if ( self.__currentCubeState == CubeState.IDLE ):
         self.__startTime = currentTime
      else:
         self.__startTime = self.__lastSimTime
      if ( self.__currentCubeState == CubeState.ROTATING ):
         self.__currentState = self.__rotationState
      elif ( self.__currentCubeState == CubeState.IDLEPULSE ):
         self.__currentState = self.__idlePulseState
      elif ( self.__currentCubeState == CubeState.IDLE ):
         self.__currentState = self.__idleState
      elif ( self.__currentCubeState == CubeState.STROBE ):
         self.__currentState = self.__strobeState
      elif ( self.__currentCubeState == CubeState.FADE ):
         self.__currentState = self.__fadeState
      elif ( self.__currentCubeState == CubeState.SPIRALFADE ):
         self.__currentState = self.__spiralFadeState
      elif ( self.__currentCubeState == CubeState.DELAY ):
         self.__currentState = self.__delayState
      self.__currentState.Start( self.__startTime, self.__queuedStates[0], self.__colors, self.__faceColors, self.__initialColorIndices ) 
      self.__queuedStates.pop( 0 )
      
   def __RemapOutputs( self, colors ):
      correctedColor = []
      for i in range( len(colors) ):
         correctedColor.append( colors[ groovikConfig.lightBoardMap[ i ] ][:] )
         for c in range(3):
            correctedColor[i][c] *= groovikConfig.colorCorrection[i][c]
      return correctedColor
         
   def __SwitchMode( self, params ):
      if ( params[0] == CubeMode.NORMAL ):
         self.__currentMode = self.__normalMode
      elif ( params[0] == CubeMode.CALIBRATION ):
         self.__currentMode = self.__calibrationMode
      elif ( params[0] == CubeMode.LIGHT_BOARD_CONFIGURATION ):
         self.__currentMode = self.__lightBoardConfiguration
      elif ( params[0] == CubeMode.SCREENSAVER ):
         self.__currentMode = self.__screensaver
      else:
         print "Unknown cube mode requested!"
      
      self.__currentCubeMode = params[0]
      
      # The mode will return the face colors to use, 
      # and the indices of the face colors of the initial configuration
      self.__faceColors, self.__initialColorIndices = self.__currentMode.StartMode( self )
      
      # if they didn't specify an initial configuration, we'll assume 
      # there are 6 face colors and each face starts with one face color
      # Note that this will function ok if there are < 6 unique face colors
      if ( self.__initialColorIndices == None ):
         self.__initialColorIndices = []
         faceColorCount = len( self.__faceColors )
         for f in range(0,6):
            for i in range(0,9):
               self.__initialColorIndices.append( f % faceColorCount )
      
      # Then we start by fading in to the initial colors
      self.__AppendState( [ CubeState.FADE, 0.5, False, self.__initialColorIndices ] ) 

   def __ClearRotationQueue( self ):
      while( len( self.__queuedStates ) ):
         self.__queuedStates.pop( 0 )
      if ( self.__currentCubeState == CubeState.IDLE ):
         self.__currentCubeState = CubeState.UNKNOWN
   
   def LogEvent( self, str ):
      if ( self.__logger != None ):
         self.__logger.logLine( str )
			
   def __AppendState(self, params):
      if ( params[0] == CubeState.IDLE ):
         raise NameError( 'Illegal to Append the IDLE state' )
      self.__queuedStates.append( params );
      #self.LogEvent( "State:" + str(params) );


