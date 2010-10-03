#-------------------------------------------------------------------------------
#
# state object used to perform the idle pulse state	
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import copy

class StateIdlePulse( StateBase ):
	def __init__(self):
		self.defaultIdlePulseDuration = 0.5
		self.idlePulseStartTime = 1.0
		self.__pulseFactor = [ 1.0, 0.5, 1.0 ]
				
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		duration = params[0]
		self.__pulseTimes = [ currentTime, currentTime + duration * 0.5, currentTime + duration ]
		self.__pulseIndex = 0
		self.__colors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		simTime = self.__ComputeNextSimTime( currentTime )
		if ( self.__pulseIndex >= 2 ):
			return [ self.__colors, simTime, True ]
		output = [ copy.deepcopy( self.__colors ), simTime, False ]
		if ( self.__pulseIndex < 2 ):
			t = ( simTime - self.__pulseTimes[ self.__pulseIndex ] ) / ( self.__pulseTimes[ self.__pulseIndex + 1 ] - self.__pulseTimes[ self.__pulseIndex ] ) 
			factor = self.__pulseFactor[ self.__pulseIndex ] + t * ( self.__pulseFactor[ self.__pulseIndex + 1 ] - self.__pulseFactor[ self.__pulseIndex ] )
			i = 0;
			while ( i < len( output[0] ) ):
				if ( self.__ShouldPulse( i ) ):
					for c in range( 0, 3 ):
						output[0][i][c] = output[0][i][c] * factor
				i = i + 1
		return output	
	
	def __ComputeNextSimTime( self, currentTime ):
		# keyframes should happen each time a pixel hits a control point
		if ( self.__pulseIndex == 2 ):
			return currentTime
		pulseTime = self.__pulseTimes[ self.__pulseIndex + 1 ]
		if ( pulseTime >= currentTime ):
			return currentTime
		self.__pulseIndex = self.__pulseIndex + 1
		return pulseTime
	
	def __ShouldPulse( self, i ):
		i = ( i / 9 )
		cornerColor = self.__colors[i * 9];
		for j in range(9):
			color = self.__colors[i * 9 + j];
			for c in range(3):
				if (cornerColor[c] != color[c]):
					return False
		return True
