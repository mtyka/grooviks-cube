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
				self.physPixel += 1
				logicalPixel = display.lm.xthPixel(self.physPixel)
				faceIndices[logicalPixel] = 0
				grooviksCube.QueueFade( 0, False, faceIndices )
				return
			logicalPixel = display.lm.xthPixel(self.physPixel)
			print "logical pixel %d" % logicalPixel
			print " params %d" % params
			display.lm.switchPixels( params, logicalPixel )
			display.lm.saveMapping()
			if ( self.physPixel < 53 ) :
				faceIndices[logicalPixel] = 1
				faceIndices[params] = 2
				if (display.lm.xthPixel(self.physPixel+1) == logicalPixel ):
					faceIndices[logicalPixel] = 2
					self.physPixel += 1 #this is if you put two faces in the right spot with one swap
				self.physPixel += 1
				logicalPixel = display.lm.xthPixel(self.physPixel)
				print "new logical pixel %d" % logicalPixel
				faceIndices[logicalPixel] = 0
				grooviksCube.QueueFade( 0, False, faceIndices )
			else:
				grooviksCube.QueueModeChange( CubeMode.NORMAL )
		
	def CanQueueState( self, grooviksCube, state ):	
		return not grooviksCube.HasQueuedStates()

	def SelectNewState( self, grooviksCube, currentTime, currentColors, stateFinished ):
		return None

