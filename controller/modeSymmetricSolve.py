#-------------------------------------------------------------------------------
#
# Interface for game modes that control cube simulations
# Only one game mode can be active at a time
#
#-------------------------------------------------------------------------------

from modenormal import *

class ModeSymmetricSolve( ModeNormal ):

	def StartMode( self, grooviksCube, difficulty="medium"):
		self.__currentDifficulty = difficulty
		self.__normalModeState = ModeNormalState.NORMAL
		return groovikConfig.standardFaceColors, None

	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		print "sym input: " + str(cubeInputType) + " " + str(params)
		if ( cubeInputType == CubeInput.ROTATION ):
			print "gets here"
			oppositeMoves = {0:2, 2:0, 3:5, 5:3, 6:8, 8:6}
			inserts = [];

			for move in params:
				print move
				if (move[0] != 1 and move[0] != 4 and move[0] != 7):
					inserts.append([params.index(move), [oppositeMoves[move[0]], move[1]]])

			print "inserts: " + str(inserts)

			for x in inserts:
				params.insert(x[0], x[1])

			print "final params: " + str(params)
			grooviksCube.QueueRotation( params )

	def Randomize(self, grooviksCube, depth, time = .5):
		self.__normalModeState = ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE
		if depth > 15:
			depth = 8
		resetScript = GScript()
		resetScript.CreateRandom(depth, time, True)
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

					clients = grooviksCube.GetAllClients()
					client_state = []
					for client in clients:
						client_state.append( client.GetState() )

					for position in [1,2,3,4]:
						push_message( json.dumps({"gamestate": "VICTORY", 'position':position, "clientstate": client_state}), 'gameState' )

		# We're done with the victory dance + randomization after we have no more queued states
		elif ( self.__normalModeState == ModeNormalState.VICTORY_DANCE ):
			if ( not grooviksCube.HasQueuedStates() ):
				# Randomize the cube now we've finished with the victory dance
				self.__normalModeState = ModeNormalState.RANDOMIZING_AFTER_VICTORY_DANCE
				resetScript = GScript()
				resetScript.CreateRandom( 8, .3, True)
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
		for i in range(6):
			cornerColor = colors[i * 9];
			for j in range(9):
				color = colors[i * 9 + j];
				for c in range(3):
					if ( cornerColor[c] != color[c] ):
						return False;
		return True;