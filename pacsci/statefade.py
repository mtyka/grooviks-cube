#-------------------------------------------------------------------------------
#
# state object used to crossfade the cube to a different state (VICTORY)	
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import copy

class StateFade( StateBase ):
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		duration = params[0]
		self.__fadeInHSL = params[1]
		
		faceColorCount = len(faceColors)		
		self.__fadeColors = []
		if ( len(params) == 2 ) or ( params[2] is None ):
			# Go back to initial state
			for i in range(54):
				faceIndex = initialColorIndices[i]
				if ( faceIndex >= 0 and faceIndex < faceColorCount ):
					self.__fadeColors.append( faceColors[faceIndex] )
				else:
					self.__fadeColors.append( [0, 0, 0] )
		elif ( len( params[2] ) == 3 ):
			singleColor = copy.deepcopy( params[2] )
			for i in range(54):
				# Single color version
				self.__fadeColors.append( singleColor )
		else:
			# Specifying a pattern to strobe to in terms of the face colors
			for faceIndex in params[2]:
				if ( faceIndex >= 0 and faceIndex < faceColorCount ):
					self.__fadeColors.append( faceColors[ faceIndex ] )
				else:
					self.__fadeColors.append( [0, 0, 0] )
		
		self.__fadeStartTime = currentTime
		self.__fadeEndTime = currentTime + duration
		self.__colors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		simTime = self.__ComputeNextSimTime( currentTime )
		if ( simTime >= self.__fadeEndTime ):
			return [ self.__fadeColors, simTime, True ]
		
		output = [ [], simTime, False ]
				
		t = ( simTime - self.__fadeStartTime ) / ( self.__fadeEndTime - self.__fadeStartTime ) 
		i = 0;
		while ( i < len( self.__colors ) ):
			if ( self.__fadeInHSL ):
				output[0].append( BlendColorsHSL( self.__colors[i], self.__fadeColors[i], t ) )
			else:
				output[0].append( BlendColorsRGB( self.__colors[i], self.__fadeColors[i], t ) )
			i = i + 1
		return output	
	
	def __ComputeNextSimTime( self, currentTime ):
		# keyframes should happen each time a pixel hits a control point
		# The only control point for a fade is the end time
		if ( self.__fadeEndTime >= currentTime ):
			return currentTime
		return self.__fadeEndTime