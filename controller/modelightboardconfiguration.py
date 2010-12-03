#-------------------------------------------------------------------------------
# 
# This mode is useful when trying to hook up the light board addresses
# to the simulation index for each cube pixel
#
#-------------------------------------------------------------------------------
from groovikconfig import *
from groovikutils import *
from modebase import ModeBase

class ModeLightBoardConfiguration( ModeBase ):		    
	def StartMode( self, grooviksCube ):
		self.__CalibrationMode = 0
		faceIndices = []
		for i in range( 54 ):
			faceIndices.append( -1 )
		faceIndices[ self.__CalibrationMode ] = 0
		return [ [ 1.0, 1.0, 1.0 ] ], faceIndices
	
	def HandleInput( self, grooviksCube, cubeInputType, params ):
		if ( cubeInputType == CubeInput.ROTATION ):
			if ( params[0][1] is False ):
				self.__CalibrationMode = self.__CalibrationMode + 1
				self.__CalibrationMode = self.__CalibrationMode % 54
			else:
				self.__CalibrationMode = self.__CalibrationMode - 1
				if ( self.__CalibrationMode < 0 ):
					self.__CalibrationMode = 53
			faceIndices = []
			for i in range( 54 ):
				faceIndices.append( -1 )
			faceIndices[ self.__CalibrationMode ] = 0
			grooviksCube.QueueFade( 0.5, False, faceIndices )
		
	def CanQueueState( self, grooviksCube, state ):	
		return not grooviksCube.HasQueuedStates()

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		return None

