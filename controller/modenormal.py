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
		# Sound 1 is the startup and scramble sound
		gs_dict = { 'soundid':'1', 'stopall':False }
		push_message( json.dumps(gs_dict), 'playsound' )

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
			
					# Play three sounds together for a intense victory sound
					# The palette are all the sounds that are not associated with key presses
					victory_palette = [4, 7, 10, 13, 16, 19, 21, 22, 23, 25, 30, 31, 32, 37, 38, 40, 41, 43, 46, 49, 52, 54, 55]
					gs_dict = { 'soundid':'', 'stopall':False }
					gs_dict["soundid"] = str(random.choice(victory_palette))
					push_message( json.dumps(gs_dict), 'playsound' )
					gs_dict["soundid"] = str(random.choice(victory_palette))
					push_message( json.dumps(gs_dict), 'playsound' )
					gs_dict["soundid"] = str(random.choice(victory_palette))
					push_message( json.dumps(gs_dict), 'playsound' )

					if grooviksCube.getDifficulty() > 15:
						groovikConfig.addLeaderboardEntry(
							int(groovikConfig.kioskSettings['mp-session-duration'])-grooviksCube.getTimeLeft(),
							grooviksCube.moves)
						groovikConfig.SaveConfig()
						groovikConfig.getLeaderboard()

					clients = grooviksCube.GetAllClients()
					client_state = []
					for client in clients:
						client_state.append( client.GetState() )

					for position in [1,2,3]:
						push_message( json.dumps({"gamestate": "VICTORY", 'position':position, "clientstate": client_state}), 'gameState' )

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
