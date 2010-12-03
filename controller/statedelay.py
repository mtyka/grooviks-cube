#-------------------------------------------------------------------------------
#
# state object used to perform the delay state	
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import copy

class StateDelay( StateBase ):
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		self.__endTime = currentTime + float( params[0] )
		self.__colors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		simTime = currentTime
		if ( currentTime >= self.__endTime ):
			simTime = self.__endTime
		output = [ self.__colors, simTime, ( simTime == self.__endTime ) ]
		return output	
	
	
