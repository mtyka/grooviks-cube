#-------------------------------------------------------------------------------
# 
# Interface for game modes that control cube simulations
# Only one game mode can be active at a time
#
#-------------------------------------------------------------------------------
from groovikconfig import *
from groovikutils import *

class ModeBase(object):	
	# This is called whenever the mode starts. The mode must return two values (comma separated)
	# First: a list of unique colors that will be visible on the cube (can be any length you want)
	# Second: an array of 54 indices into that list of unique colors to use as an initial condition
	# for the cube pixels. -1 is a valid element of the indices, and indicates that the pixel should be black
	def StartMode( self, grooviksCube ):
		raise NotImplementedError
	
	# This is called whenever an input event is posted to the goovik simulation object.
	# cubeInputType is an enum in the CubeInput python class. Params is a input-type specific
	# piece of data (described in the CubeInput python class comments).
	# The simulation object handles the mode switch input and forwards all others to the game mode
	# Here, the game mode can respond to the input event by queueing a state change onto the simulation object.
	# Typically, you'd call methods like grooviksCube.QueueFade() or grooviksCube.QueueRotation().
	# There are no return values from this function.
	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		raise NotImplementedError

	# Every simulation step, this method is called to check if it wants to queue a new state 
	# change on the simulation object. For example, the game mode can detect here if the cube 
	# is solved and switch to a victory condition.
	# currentTime is the current simulation time. currentColors is the *non-color corrected*
	# colors at that simulation time. stateFinished indicates whether the current cube state has
	# just completed in this simulation timestep. The grooviksCube class can be used to query
	# other data, such as current state.
	# There are no return values from this function.
	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		raise NotImplementedError
	
	#	Every time a state change is about to be queued on the simulation object, this method is called 
	# to see if it will allow the state change to be queued. This is used to allow the game mode 
	# to suppress state changes while in its victory mode, for example. The state argument
	# is the CubeState enum, indicating the state about to be queued if CanQueueState returns True.
	# If CanQueueState returns False, the state will not be queued.
	def CanQueueState( self, grooviksCube, state ):	
		raise NotImplementedError

