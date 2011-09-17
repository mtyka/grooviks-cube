#-------------------------------------------------------------------------------
# 
# This mode is used to adjust the color calibration settings
#
#-------------------------------------------------------------------------------
from groovikconfig import *
from groovikutils import *
from modebase import ModeBase

class ModeCalibration( ModeBase ):
	def StartMode( self, grooviksCube ):
		self.__CalibrationMode = 0
		faceIndices = []
		for i in range( 54 ):
			faceIndices.append( 0 )
		return groovikConfig.calibrationColors, faceIndices
	
	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		if ( cubeInputType == CubeInput.ROTATION ):
			self.__CalibrationMode = self.__CalibrationMode + 1
			self.__CalibrationMode = self.__CalibrationMode % len(groovikConfig.calibrationColors)
			grooviksCube.QueueFade( 0.5, False, groovikConfig.calibrationColors[self.__CalibrationMode] )
		
	def CanQueueState( self, grooviksCube, state ):	
		return not grooviksCube.HasQueuedStates()

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		return None
