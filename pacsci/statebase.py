#-------------------------------------------------------------------------------
#
# Interface for state objects that affect cube simulation
# Only one state object can be active at a time
#
#-------------------------------------------------------------------------------
class StateBase:
	# This is called when you entry this state. You are passed the following state:
	# currentTime: the current simulation time in seconds
	# params: initialization parameters (state dependent)
	# startingColors: stores the cube's initial state as an array of 54 colors
	# faceColors: a list of the unique colors of the cube (usually 6 colors, but can be any #).
	#    Each color is a tuple [r, g, b] stored as floating point numbers.
	# initialColorIndices: an array of indices into the faceColors arrayrs
	#   representing the colors of each cube pixels in the curernt mode's initial state
	#   -1 in these indices represents the color of that pixel should be black.
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		raise NotImplementedError
	
	# Simulate to the next "important" time or current time, which ever comes first
	# Update returns a list; first element is a list containing the 54 cube face colors (stored as [r, g, b] tuples).
	# The second element is time up to which this invocation of Update() has simulated,
	# which is <= currentTime. The reason why we may not want to simulate up to current time
	# is because there are times we want to return keyframes which we want the lightboards
	# to exactly match, for example, when, during a rotation, we've rotated 
	# exactly an integral # of faces to the left/right.
	# 3rd element is whether the state is done
	def Update( self, currentTime ):
		raise NotImplementedError
