#-------------------------------------------------------------------------------
#
# state object used to spiral fade the cube to a different state (VICTORY)	
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import copy

class StateSpiralFade( StateBase ):
	def __init__(self):
		self.__spiralFadeOrder = [
			[ 4, 5, 8, 7, 6, 3, 0, 1, 2, 18, 21, 24, 44, 41, 38, 35, 32, 29, 45, 48, 51, 19, 22, 25, 43, 40, 37, 34, 31, 28, 46, 49, 52, 20, 23, 26, 42, 39, 36, 33, 30, 27, 47, 50, 53, 9, 12, 15, 16, 17, 14, 11, 10, 13 ], # xaxis
			[ 22, 23, 26, 25, 24, 21, 18, 19, 20, 9, 12, 15, 42, 43, 44, 8, 5, 2, 51, 52, 53, 10, 13, 16, 39, 40, 41, 7, 4, 1, 48, 49, 50, 11, 14, 17, 36, 37, 38, 6, 3, 0, 45, 46, 47, 27, 30, 33, 34, 35, 32, 29, 28, 31 ], # yaxis
			[ 40, 41, 44, 43, 42, 39, 36, 37, 38, 6, 7, 8, 24, 25, 26, 15, 16, 17, 33, 34, 35, 3, 4, 5, 21, 22, 23, 12, 13, 14, 30, 31, 32, 0, 1, 2, 18, 19, 20, 9, 10, 11, 27, 28, 29, 45, 48, 51, 52, 53, 50, 47, 46, 49 ] # zaxis
		]		
		
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		duration = params[0]
		self.__fadeAxis = params[1]
		self.__fadeInHSL = params[2]

		# Fastest the arduinos can take it
		duration = max( duration, TIMESTEP * 9 )
		
		faceColorCount = len(faceColors)		
		self.__fadeColors = []
		if ( len(params) == 3 ) or ( params[3] is None ):
			# Go back to initial state
			for i in range(54):
				faceIndex = initialColorIndices[i]
				if ( faceIndex >= 0 and faceIndex < faceColorCount ):
					self.__fadeColors.append( faceColors[faceIndex] )
				else:
					self.__fadeColors.append( [0, 0, 0] )
		elif ( len( params[3] ) == 3 ):
			singleColor = copy.deepcopy( params[3] )
			for i in range(54):
				# Single color version
				self.__fadeColors.append( singleColor )
		else:
			# Specifying a pattern to strobe to in terms of the face colors
			for faceIndex in params[3]:
				if ( faceIndex >= 0 and faceIndex < faceColorCount ):
					self.__fadeColors.append( faceColors[ faceIndex ] )
				else:
					self.__fadeColors.append( [0, 0, 0] )
		
		self.__fadeStartTime = currentTime
		self.__fadeDuration = float( duration ) / 54.0
		self.__fadeSegmentStartTime = currentTime
		self.__fadeNextTime = self.__fadeStartTime + self.__fadeDuration
		self.__fadeIndex = 0
		self.__colors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		simTime = self.__ComputeNextSimTime( currentTime )
		if ( self.__fadeIndex >= 54 ):
			return [ self.__fadeColors, simTime, True ]
		
		output = [ [], simTime, False ]
		
		indices = self.__spiralFadeOrder[ self.__fadeAxis ]
		t = ( simTime - self.__fadeSegmentStartTime ) / ( self.__fadeNextTime - self.__fadeSegmentStartTime ) 
		i = 0;
		while ( i < len( self.__colors ) ):
			index = indices.index( i )
			if ( index < self.__fadeIndex ):
				output[0].append( self.__fadeColors[i] )
			elif ( index > self.__fadeIndex ):
				output[0].append( self.__colors[i] )
			else:
				if ( self.__fadeInHSL ):
					output[0].append( BlendColorsHSL( self.__colors[i], self.__fadeColors[i], t ) )
				else:
					output[0].append( BlendColorsRGB( self.__colors[i], self.__fadeColors[i], t ) )
			i = i + 1
		return output	
	
	def __ComputeNextSimTime( self, currentTime ):
		# keyframes should happen each time a pixel hits a control point
		# The only control point for a fade is the end time
		if ( self.__fadeIndex >= 54 ):
			return currentTime
		if ( self.__fadeNextTime >= currentTime ):
			return currentTime
		simTime = self.__fadeNextTime
		self.__fadeSegmentStartTime = self.__fadeNextTime
		self.__fadeNextTime = self.__fadeNextTime + self.__fadeDuration
		self.__fadeIndex = self.__fadeIndex + 1
		return simTime