#-------------------------------------------------------------------------------
#
# Interface for game modes that control cube simulations
# Only one game mode can be active at a time
#
#-------------------------------------------------------------------------------

from modenormal import *

class ModePartialSolveState(ModeNormalState):
	easy = [6, 0,6, 0, 0, 0,6, 0,6,	#R 0-8
			6,6,6,6, 1,6,6,6,6,	#L 9-17
			6,6,6,6, 2,6,6,6,6,	#F 18-26
			6,6,6,6, 3,6,6,6,6,	#B 27-35
			6,6,6,6, 4,6,6,6,6,	#U 36-44
			6,6,6,6, 5,6,6,6,6] #D 45-53

	medium = [ 0, 0, 0, 0, 0, 0, 0, 0, 0,
			  6,6,6,6, 1,6,6,6,6,
			  6,6,6,6, 2,6,6,6,6,
			  6,6,6,6, 3,6,6,6,6,
			  6,6,6,6, 4,6,6,6,6,
			  6,6,6,6, 5,6,6,6,6]

	hard = [0, 0, 0, 0, 0, 0, 0, 0, 0,	#R
			  6, 6, 6, 6, 1, 6, 6, 6, 6,	#L
			  2, 6, 6, 2, 2, 6, 2, 6, 6,	#F
			  6, 6, 3, 6, 3, 3, 6, 6, 3,	#B
			  6, 6, 4, 6, 4, 4, 6, 6, 4,	#U
			  5, 6, 6, 5, 5, 6, 5, 6, 6]

class ModePartialSolve( ModeNormal ):

	__difficulties = {"easy": 2,
		"medium": 3,
		  "hard": 4,
		}

	__initialStates = {"easy": ModePartialSolveState.easy,
		"medium": ModePartialSolveState.medium,
		  "hard": ModePartialSolveState.hard,
		}

	def StartMode( self, grooviksCube, difficulty="medium"):
		self.__currentDifficulty = difficulty
		self.__normalModeState = ModePartialSolveState.NORMAL
		return groovikConfig.standardFaceColors, self.__initialStates[difficulty];

	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		if ( cubeInputType == CubeInput.ROTATION ):
			grooviksCube.QueueRotation( params )

	def Randomize(self, grooviksCube, depth, time = .5):
		self.__normalModeState = ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE
		depth = self.difficulties[self.__currentDifficulty]
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

	def CanQueueState( self, grooviksCube, state ):
		if ( self.__normalModeState != ModeNormalState.NORMAL ):
			return False
		if ( grooviksCube.HasQueuedStates() ):
			return False
		return True

	def __Solved(self, colors):
		if (self.__currentDifficulty == "easy"):
			return self.easyIsSolved(colors)
		elif (self.__currentDifficulty == "medium"):
			return self.mediumIsSolved(colors)
		elif (self.__currentDifficulty == "hard"):
			return self.hardIsSolved(colors)
		elif (self.__currentDifficulty == "harder"):
			return self.harderIsSolved(colors)
		else:
			return False


	def easyIsSolved(self, colors):
		solvedSide = self.__convertStickersToColors([[6,0,6,0,0,0,6,0,6]])[0]
		for i in range(6):
			subset = colors[i*9:i*9+9]
			if (subset == solvedSide):
				return True

		return False


	def mediumIsSolved(self, colors):
		solvedSide = self.__convertStickersToColors([[0]*9])[0]
		for i in range(6):
			subset = colors[i*9:i*9+9]
			if (subset == solvedSide):
				return True

		return False

	def hardIsSolved(self, colors):
		pattern = self.__convertStickersToColors([[6,0,6,0,0,0,6,0,6]])[0]
		location = self.findSide(pattern)
		if (location < 0):
			return False

		for i in range(6):
			subset = colors[i*9:i*9+9]
			if (not self.sideHasOneColor(subset)):
				return False

		return True


	def harderIsSolved(self, colors):
		pattern = self.__convertStickersToColors([[0]*9])[0]
		location = self.findSide(pattern)
		if (location < 0):
			return False

		for i in range(6):
			subset = colors[i*9:i*9+9]
			if (not self.sideHasOneColor(subset)):
				return False

		return True

	def __convertStickersToColors(self, side):
		ret = []
		for stickers in side:
			perm = []
			for s in stickers:
				perm.append(groovikConfig.standardFaceColors[s])

			ret.append(perm)
		return ret

	def findSide (self, pattern, colors):
		for i in range(6):
			subset = colors[i*9:i*9+9]
			if (subset == pattern):
				return i

		return -1

	def sideHasOneColor(self, s):
		primer = -10
		for i in s:
			if (i != -1 and primer < 0):
				primer = i
			elif (i != primer and i != -1):
				return False

		return True