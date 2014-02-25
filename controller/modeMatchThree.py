#-------------------------------------------------------------------------------
#
# Interface for game modes that control cube simulations
# Only one game mode can be active at a time
#
#-------------------------------------------------------------------------------

from modenormal import *

class ModePartialSolveState(ModeNormalState):
	easy = [0,0,0,6,6,6,6,6,6,	#R 0-8
		   	6,6,6,6,6,6,6,6,6,	#L 966
		   	6,6,6,6,6,6,6,6,6,	#F 18-26
		   	6,6,6,6,6,6,6,6,6,	#B 26-35
		   	6,6,6,6,6,6,6,6,6,	#U 36-44
		   	6,6,6,6,6,6,6,6,6]  #D 45-53

	#this might be too hard for players... unsure.
	medium = [0,0,0,6,6,6,6,6,6,	#R 0-8
			  6,6,6,6,6,6,6,6,6,	#L 966
			  3,6,6,6,6,6,6,6,6,	#F 18-26
			  6,6,2,6,6,6,6,6,6,	#B 26-35
			  6,6,6,6,6,6,6,6,6,	#U 36-44
			  1,6,6,1,6,6,1,6,6] 	#D 45-53

class ModeMatchThree( ModeNormal ):

	__initialStates = {
		  "easy": ModePartialSolveState.easy,
		"medium": ModePartialSolveState.medium,
	}

	def StartMode( self, grooviksCube, difficulty="easy"):
		self.__currentDifficulty = difficulty
		self.__normalModeState = ModePartialSolveState.NORMAL
		return groovikConfig.standardFaceColors, self.__initialStates[self.__currentDifficulty]

	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		if ( cubeInputType == CubeInput.ROTATION ):
			grooviksCube.QueueRotation( params )

	def Randomize(self, grooviksCube, depth, time = .5):
		self.__normalModeState = ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE
		depth = self.difficulties[self.__currentDifficulty]
		resetScript = GScript()
		resetScript.CreateRandom(depth, time)
		resetScript.ForceQueue( grooviksCube )

	def SetDifficulty(self, diff):
		if diff == 2:
			self.__currentDifficulty = "easy"
			return self.__initialColorIndices[self.__currentDifficulty]
		elif diff == 4:
			self.__currentDifficulty = "medium"

		return self.__initialStates[self.__currentDifficulty]

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

	def CanQueueState( self, grooviksCube, state ):
		if ( self.__normalModeState != ModeNormalState.NORMAL ):
			return False
		if ( grooviksCube.HasQueuedStates() ):
			return False
		return True

	def __Solved(self, colors):
		#print "match 3 colors:  " + "".join(str(x) for x in colors)
		if self.__currentDifficulty is "easy":
			return self.__easyIsSolved(colors)
		elif self.currentDifficulty is "medium":
			return self.__mediumIsSolved(colors)

	def __easyIsSolved(self, colors):
		solvedStates = self.__convertStickersToColors(
						[[0,0,0,6,6,6,6,6,6],
						 [0,6,6,0,6,6,0,6,6],
						 [6,6,6,6,6,6,0,0,0],
						 [6,6,0,6,6,0,6,6,0]])

		for i in solvedStates:
			if (self.__findSide(i,colors) >= 0):
				return True

		return False

	def __mediumIsSolved(self, colors):
		solvedStates1 = self.__convertStickersToColors(
						[[0,0,0,6,6,6,6,6,6],
						 [0,6,6,0,6,6,0,6,6],
						 [6,6,6,6,6,6,0,0,0],
						 [6,6,0,6,6,0,6,6,0]])

		solvedStates2 = self.__convertStickersToColors(
						[[1,1,1,6,6,6,6,6,6],
						 [1,6,6,1,6,6,1,6,6],
						 [6,6,6,6,6,6,1,1,1],
						 [6,6,1,6,6,1,6,6,1]])

		state1 = False
		state2 = False

		for i in solvedStates1:
			if (self.__findSide(i,colors) >= 0):
				state1 = True
				break

		for i in solvedStates2:
			if (self.__findSide(i,colors) >= 0):
				state2 = True;
				break;

		return state1 and state2

	def __convertStickersToColors(self, side):
		ret = []
		for stickers in side:
			perm = []
			for s in stickers:
				perm.append(groovikConfig.standardFaceColors[s])

			ret.append(perm)
		return ret

	def __findSide(self, pattern, colors):
		for i in range(6):
			if colors[i*9:i*9+9] == pattern:
				return i

		return -1