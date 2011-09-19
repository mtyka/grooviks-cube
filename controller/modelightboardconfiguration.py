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
		self.physPixel = -1
		faceIndices = []
		for i in range( 54 ):
			faceIndices.append( 1 )
		return [ [ 1.0, 0, 0 ], [0, 1, 0 ], [ 0.0, 0.0, 1.0 ] ], faceIndices
	
	def HandleInput( self, grooviksCube, display, cubeInputType, params ):
		if ( cubeInputType == CubeInput.FACE_CLICK ):
			faceIndices = grooviksCube.GetFaceColorIndicies()
			if (self.physPixel == -1 ):
				faceIndices.append(0)
				self.physPixel += 1
				logicalPixel = display.lm.xthPixel(self.physPixel)
				faceIndices[logicalPixel] = 0
				grooviksCube.QueueFade( 0, False, faceIndices[:-1] )
				return
			logicalPixel = display.lm.xthPixel(self.physPixel)
			display.lm.switchPixels( params, logicalPixel )
			display.lm.saveMapping()
			if ( self.physPixel < 55 ) :
				faceIndices[logicalPixel] = 1
				faceIndices[params] = 2
				self.physPixel += 1
				logicalPixel = display.lm.xthPixel(self.physPixel)
				faceIndices[logicalPixel] = 0
				print len(faceIndices[:-1])
				grooviksCube.QueueFade( 0, False, faceIndices[:-1] )
			else:
				grooviksCube.QueueModeChange( CubeMode.NORMAL )
		
	def CanQueueState( self, grooviksCube, state ):	
		return not grooviksCube.HasQueuedStates()

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		return None

