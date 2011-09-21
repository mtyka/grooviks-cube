#-------------------------------------------------------------------------------
# 
# This mode is used to adjust the color calibration settings
#
#-------------------------------------------------------------------------------
from groovikconfig import *
from groovikutils import *
from modebase import ModeBase
import time

class ModeScreenSaver( ModeBase ):
	def StartMode( self, grooviksCube ):
		self.__Color = 0
		faceIndices = []
		for i in range( 54 ):
			faceIndices.append( 1 )
		return groovikConfig.calibrationColors, faceIndices
	
	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		self.__Color = self.__Color + 1
		self.__Color = self.__Color % len(groovikConfig.calibrationColors)
		grooviksCube.QueueFade( 0.5, False, groovikConfig.calibrationColors[self.__Color] )
		
	def CanQueueState( self, grooviksCube, state ):	
		return not grooviksCube.HasQueuedStates()

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		self.__Color = self.__Color + 1
		self.__Color = self.__Color % len(groovikConfig.calibrationColors)
		grooviksCube.QueueFade( 0.5, False, groovikConfig.calibrationColors[self.__Color] )
