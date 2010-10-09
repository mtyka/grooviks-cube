#-------------------------------------------------------------------------------
#
# state object used to strobe the cube (VICTORY)	
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import copy

class StateStrobe( StateBase ):
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		duration = params[0]
		strobeDuration = params[1]
		self.__strobeInHSL = params[2]
		
		if ( len( params[3] ) == 3 ):
			# Single color version
			self.__strobeColor = copy.deepcopy( params[3] )
			self.__singleStrobeColor = True
		else:
			# Specifying a pattern to strobe to in terms of the face colors
			faceColorCount = len(faceColors)			
			self.__strobeColor = []
			for faceIndex in params[3]:
				if ( faceIndex >= 0 and faceIndex < faceColorCount ):
					self.__strobeColor.append( faceColors[ faceIndex ] )
				else:
					self.__strobeColor.append( [0, 0, 0] )
			self.__singleStrobeColor = False
		
		# Can't go below 166 / 3, too much data for arduinos
		# (need control points when dark + light, get one for each strobe)
		strobeDuration = max( strobeDuration, TIMESTEP / 3.0 ) 
		count = int( duration / strobeDuration )
		self.__strobeTimes = []
		self.__strobeFactors = []
		self.__strobeControlPointCount = 2 * count + 1
		strobeTime = currentTime;
		strobeFactor = 1.0
		for i in range( 0, self.__strobeControlPointCount ):
			self.__strobeTimes.append( strobeTime )
			self.__strobeFactors.append( strobeFactor )
			strobeTime = strobeTime + strobeDuration
			strobeFactor = 1.0 - strobeFactor	
		self.__strobeIndex = 0
		self.__colors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		simTime = self.__ComputeNextSimTime( currentTime )
		if ( self.__strobeIndex >= self.__strobeControlPointCount - 1 ):
			return  [ self.__colors, simTime, True ]
		output = [ [], simTime, False ]
		t = ( simTime - self.__strobeTimes[ self.__strobeIndex ] ) / ( self.__strobeTimes[ self.__strobeIndex + 1 ] - self.__strobeTimes[ self.__strobeIndex ] ) 
		factor = self.__strobeFactors[ self.__strobeIndex ] + t * ( self.__strobeFactors[ self.__strobeIndex + 1 ] - self.__strobeFactors[ self.__strobeIndex ] )
		i = 0;
		while ( i < len( self.__colors ) ):
			if ( self.__singleStrobeColor ):
				strobeColor = self.__strobeColor
			else:
				strobeColor = self.__strobeColor[i]
			if ( self.__strobeInHSL ):
				output[0].append( BlendColorsHSL( strobeColor, self.__colors[i], factor ) )
			else:
				output[0].append( BlendColorsRGB( strobeColor, self.__colors[i], factor ) )
			i = i + 1
		return output	
	
	def __ComputeNextSimTime( self, currentTime ):
		# keyframes should happen each time a pixel hits a control point
		if ( self.__strobeIndex >= self.__strobeControlPointCount - 1 ):
			return currentTime
		strobeTime = self.__strobeTimes[ self.__strobeIndex + 1 ]
		if ( strobeTime >= currentTime ):
			return currentTime
		self.__strobeIndex = self.__strobeIndex + 1
		return strobeTime

