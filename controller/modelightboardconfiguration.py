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
		self.currentFace = 0
		faceIndices = []
		for i in range( 54 ):
			faceIndices.append( 1 )
		faceIndices[ self.currentFace ] = 0 
		return [ [ 1.0, 1.0, 1.0 ], [1.0, 0.0, 1.0 ], [ 0.0, 0.0, 1.0 ] ], faceIndices
	
	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		if ( cubeInputType == CubeInput.FACE_CLICK ):
			display.lm.switchPixels( params, self.currentFace )
			faceIndices = grooviksCube.GetFaceColorIndicies()
			if ( self.currentFace < 52 ) :
				faceIndices[self.currentFace] = 2
				self.currentFace += 1
				faceIndices[self.currentFace] = 0
				grooviksCube.QueueFade( 0, False, faceIndices )
			else:
				grooviksCube.QueueModeChange( CubeMode.NORMAL )
		
	def CanQueueState( self, grooviksCube, state ):	
		return not grooviksCube.HasQueuedStates()

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		return None

