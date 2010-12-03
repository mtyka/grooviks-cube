#-------------------------------------------------------------------------------
#
# state object used to perform the idle state	
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import copy

class StateIdle( StateBase ):
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		self.__targetcolors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		output = [ self.__targetcolors, currentTime, False ]
		return output	
