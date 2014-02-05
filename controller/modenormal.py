#-------------------------------------------------------------------------------
#
# This mode represents the normal operation of the cube
#
#-------------------------------------------------------------------------------
import random
from groovikconfig import *
from groovikutils import *
from GScript import GScript
from modebase import ModeBase
import json
from hbclient import *

class ModeNormalState(object):
	NORMAL = 0
	VICTORY_DANCE = 1
	RANDOMIZING_AFTER_VICTORY_DANCE = 2

class ModeNormal( ModeBase ):

	def StartMode( self, grooviksCube ):
		self.__normalModeState = ModeNormalState.NORMAL
		return groovikConfig.standardFaceColors, None

	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		if ( cubeInputType == CubeInput.ROTATION ):
			grooviksCube.QueueRotation( params )

	def CanQueueState( self, grooviksCube, state ):
		if ( self.__normalModeState != ModeNormalState.NORMAL ):
			return False
		if ( grooviksCube.HasQueuedStates() ):
			return False
		return True

	def Randomize(self, grooviksCube, depth, time = .5):
		self.__normalModeState = ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE
		resetScript = GScript()
		resetScript.CreateRandom(depth, time)
		resetScript.ForceQueue( grooviksCube )

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		# We don't do anything when the state isn't finished
		if ( stateFinished is False ):
			return

		# If we're rotating, and it's solved in normal mode, victory!
		if ( self.__normalModeState == ModeNormalState.NORMAL ):
			if ( grooviksCube.GetCurrentState() == CubeState.ROTATING ):
				if ( self.__Solved( currentColors ) ):
					self.__normalModeState = ModeNormalState.VICTORY_DANCE
					grooviksCube.QueueEffect( "victory%d"%( random.randint(0,2)) )
					gs_dict = { 'soundid':'victory1', 'stopall':False }
					print "Pushed: ", [ json.dumps(gs_dict), 'playsound']
					push_message( json.dumps(gs_dict), 'playsound' )

		# We're done with the victory dance + randomization after we have no more queued states
		elif ( self.__normalModeState == ModeNormalState.VICTORY_DANCE ):
			if ( not grooviksCube.HasQueuedStates() ):
				# Randomize the cube now we've finished with the victory dance
				self.__normalModeState = ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE
				resetScript = GScript()
				resetScript.CreateRandom( 8, .3)
				resetScript.ForceQueue( grooviksCube )
				## also make all clients quit!
				for position in [1,2,3]:
				  push_message( json.dumps({ 'position':position, 'command':ClientCommand.QUIT, }), 'clientcommand' )
		elif ( self.__normalModeState == ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE ):
			if ( not grooviksCube.HasQueuedStates() ):
				self.__normalModeState = ModeNormalState.NORMAL

	def __Solved( self, colors ):
		for i in range(6):
			cornerColor = colors[i * 9];
			for j in range(9):
				color = colors[i * 9 + j];
				for c in range(3):
					if ( cornerColor[c] != color[c] ):
						return False;
		return True;
