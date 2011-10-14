#-------------------------------------------------------------------------------
#
# State object used to perform cube rotation
#
#-------------------------------------------------------------------------------
from groovikutils import *
from groovikconfig import *
from statebase import *
import copy

class StateRotation( StateBase ):
	def __init__(self):
		self.__rotdesc3step = [
			[ 18, 21, 24, 44, 41, 38, 35, 32, 29, 45, 48, 51, 18, -1 ], # x axis
			[ 19, 22, 25, 43, 40, 37, 34, 31, 28, 46, 49, 52, 19, -1 ],
			[ 20, 23, 26, 42, 39, 36, 33, 30, 27, 47, 50, 53, 20, -1 ],
			[  9, 12, 15, 42, 43, 44,  8,  5,  2, 51, 52, 53, 9,  -1 ], # y axis
			[ 10, 13, 16, 39, 40, 41,  7,  4,  1, 48, 49, 50, 10, -1 ],
			[ 11, 14, 17, 36, 37, 38,  6,  3,  0, 45, 46, 47, 11, -1 ],
			[  6, 7,  8,  24, 25, 26, 15, 16, 17, 33, 34, 35,  6, -1 ], # z axis
			[  3, 4,  5,  21, 22, 23, 12, 13, 14, 30, 31, 32,  3, -1 ],
			[  0, 1,  2,  18, 19, 20,  9, 10, 11, 27, 28, 29,  0, -1 ], 
			[ 18, 21, 24, 44, 41, 38, 35, 32, 29, 45, 48, 51, 18, 9999, 19, 52, 49, 46, 28, 31, 34, 37, 40, 43, 25, 22, 19, 9999, 20, 23, 26, 42, 39, 36, 33, 30, 27, 47, 50, 53, 20, -1 ] # special 1
		]		
		self.__rotdesc2step = [
			[ 0, 1, 2, 5, 8, 7, 6, 3, 0, -1 ], # x axis
			[ -1, -1 ],
			[ 9, 12, 15, 16, 17, 14, 11, 10, 9, -1 ],
			[ 18, 19, 20, 23, 26, 25, 24, 21, 18, -1 ], # y axis
			[ -1, -1 ],
			[ 27, 30, 33, 34, 35, 32, 29, 28, 27, -1 ],
			[ 36, 37, 38, 41, 44, 43, 42, 39, 36, -1 ], # z axis
			[ -1, -1 ],
			[ 45, 48, 51, 52, 53, 50, 47, 46, 45, -1 ], 
			[ 0, 1, 2, 5, 8, 7, 6, 3, 0, 9999, 9, 12, 15, 16, 17, 14, 11, 10, 9, -1 ], # special 1 (same as the 'all about x')
			[ 18, 19, 20, 23, 26, 25, 24, 21, 18, 9999, 27, 30, 33, 34, 35, 32, 29, 28, 27, -1 ], # special 1 (same as the 'all about y')
			[ 6, 7, 8, 24, 25, 26, 15, 16, 17, 33, 34, 35, 6, 9999, 3, 4, 5, 21, 22, 23, 12, 13, 14, 30, 31, 32, 3, 9999, 0, 1, 2, 18, 19, 20, 9, 10, 11, 27, 28, 29, 0, -1 ],
		]
		self.__dim = [
			[ 0, 0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 1, 1, 1, 1, 1, 1,  0, 1, 1, 0, 1, 1, 0, 1, 1,  1, 1, 0, 1, 1, 0, 1, 1, 0,  1, 1, 0, 1, 1, 0, 1, 1, 0,  0, 1, 1, 0, 1, 1, 0, 1, 1 ], # x axis
			[ 1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 0, 1, 1, 0, 1, 1, 0, 1,  1, 0, 1, 1, 0, 1, 1, 0, 1,  1, 0, 1, 1, 0, 1, 1, 0, 1,  1, 0, 1, 1, 0, 1, 1, 0, 1 ],
			[ 1, 1, 1, 1, 1, 1, 1, 1, 1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 0, 1, 1, 0, 1, 1, 0,  0, 1, 1, 0, 1, 1, 0, 1, 1,  0, 1, 1, 0, 1, 1, 0, 1, 1,  1, 1, 0, 1, 1, 0, 1, 1, 0 ],
	
			[ 1, 1, 0, 1, 1, 0, 1, 1, 0,  0, 1, 1, 0, 1, 1, 0, 1, 1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 0, 0, 0,  1, 1, 1, 1, 1, 1, 0, 0, 0 ], # y axis
			[ 1, 0, 1, 1, 0, 1, 1, 0, 1,  1, 0, 1, 1, 0, 1, 1, 0, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 0, 0, 0, 1, 1, 1,  1, 1, 1, 0, 0, 0, 1, 1, 1 ],
			[ 0, 1, 1, 0, 1, 1, 0, 1, 1,  1, 1, 0, 1, 1, 0, 1, 1, 0,  1, 1, 1, 1, 1, 1, 1, 1, 1,  0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 1, 1, 1, 1, 1, 1,  0, 0, 0, 1, 1, 1, 1, 1, 1 ],

			[ 1, 1, 1, 1, 1, 1, 0, 0, 0,  1, 1, 1, 1, 1, 1, 0, 0, 0,  1, 1, 1, 1, 1, 1, 0, 0, 0,  1, 1, 1, 1, 1, 1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 1, 1, 1, 1, 1, 1, 1 ], # z axis
			[ 1, 1, 1, 0, 0, 0, 1, 1, 1,  1, 1, 1, 0, 0, 0, 1, 1, 1,  1, 1, 1, 0, 0, 0, 1, 1, 1,  1, 1, 1, 0, 0, 0, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1 ],
			[ 0, 0, 0, 1, 1, 1, 1, 1, 1,  0, 0, 0, 1, 1, 1, 1, 1, 1,  0, 0, 0, 1, 1, 1, 1, 1, 1,  0, 0, 0, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1, 1, 1,  0, 0, 0, 0, 0, 0, 0, 0, 0 ],
		]	
			
		self.rotationTime = 1.0
		self.activeRotationTime = self.rotationTime		
		self.__dimFadeTime = 0.3
			
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		self.__step2Index = self.__step3Index = 0
		self.__activeRotations = copy.deepcopy( params[0] )
		if ( len(params) >= 2 ):
			if ( params[1] >= 0 ):
				self.activeRotationTime = params[1]
			else:
				self.activeRotationTime = self.rotationTime	
			# Protect against speeds which are too fast for the arduinos to handle
			if ( self.activeRotationTime < TIMESTEP ):
				self.activeRotationTime = TIMESTEP
		else:
			self.activeRotationTime = self.rotationTime
	
		if ( len(params) >= 3 ):
			self.__doFade = params[2]
		else:
			self.__doFade = False
			
		stepTime3 = self.activeRotationTime / 3.0
		stepTime2 = self.activeRotationTime / 2.0
		
		self.__colors = copy.deepcopy( startingColors )
		self.__targetcolors = copy.deepcopy( startingColors )
		for i in range( len(self.__activeRotations) ):
			self.__RotateTargetState( self.__rotdesc3step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
			self.__RotateTargetState( self.__rotdesc2step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
		self.__step2Times = [ currentTime, currentTime + stepTime2, currentTime + self.activeRotationTime, currentTime + self.activeRotationTime ]
		self.__step3Times = [ currentTime, currentTime + stepTime3, currentTime + stepTime3 * 2.0, currentTime + self.activeRotationTime, currentTime + self.activeRotationTime ]
		
	def Update( self, currentTime ):
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		simTime = self.__ComputeNextSimTime( currentTime )

		# tracks how far along in the cube rotation we are
		rotationStep = self.__step3Index		

		# Update the target rotation state ( 3 step )
		if ( self.__step3Index < 3 ):
			t = ( simTime - self.__step3Times[ self.__step3Index ] ) / ( self.__step3Times[ self.__step3Index + 1 ] - self.__step3Times[ self.__step3Index ] )
		else:
			t = 0.0
			
		for i in range( len(self.__activeRotations) ):	
			indices = self.__rotdesc3step[ self.__activeRotations[i][0] ]
			self.__BlendTargetState( t, indices, self.__activeRotations[i][1] )
		
		# Update the target rotation state ( 2 step )	
		if ( self.__step2Index < 2 ):
			t = ( simTime - self.__step2Times[ self.__step2Index ] ) / ( self.__step2Times[ self.__step2Index + 1 ] - self.__step2Times[ self.__step2Index ] )
		else:
			t = 0.0
		for i in range( len(self.__activeRotations) ):	
			indices = self.__rotdesc2step[ self.__activeRotations[i][0] ]		
			self.__BlendTargetState( t, indices, self.__activeRotations[i][1] )
		
		output = [ copy.deepcopy( self.__colors ), rotationStep,  simTime, ( self.__step2Index == 2 and self.__step3Index == 3 ) ]
		
		# dim out non-rotating cubes, but not while in victory
		if ( self.__doFade and ( self.__step3Index < 3 ) and ( self.__step2Index < 2 ) ):
			dimFactor = groovikConfig.idlePulseDimFactor
			if ( simTime - self.__step3Times[0] < self.__dimFadeTime ):
				t = ( simTime - self.__step3Times[0] ) / self.__dimFadeTime
				dimFactor = 1.0 + ( groovikConfig.idlePulseDimFactor - 1.0 ) * t
			elif ( self.__step3Times[3] - simTime < self.__dimFadeTime ):	
				t = ( self.__step3Times[3] - simTime ) / self.__dimFadeTime
				dimFactor = 1.0 + ( groovikConfig.idlePulseDimFactor - 1.0 ) * t
			for i in range( 54 ):
				dim = True
				for j in range( len(self.__activeRotations) ):
					if ( not self.__dim[ self.__activeRotations[j][0] ][i] ):
						dim = False
				if ( dim is True ):		
					for c in range( 3 ):
						output[0][i][c] = output[0][i][c] * dimFactor
		return output
	
	def DoDirectRotation( self, colors, slice, direction ):
		
		newcolors = copy.deepcopy( colors )
		# first rotate 3step band:
		ifrom = 0
		ito = 3
		while( self.__rotdesc3step[slice][ifrom+1] >= 0 ):
			# wrap around array end
			if self.__rotdesc3step[slice][ito] < 0: ito = 1
			#print ifrom, ito
			if direction == 0:  colors[ self.__rotdesc3step[slice][ifrom] ] = copy.deepcopy(newcolors [ self.__rotdesc3step[slice][ito] ] )
			else:               colors[ self.__rotdesc3step[slice][ito] ] = copy.deepcopy(newcolors [ self.__rotdesc3step[slice][ifrom] ] )
			ito += 1
			ifrom += 1
		
		ifrom = 0
		ito = 2
		while( self.__rotdesc2step[slice][ifrom+1] >= 0 ):
			# wrap around array end
			if self.__rotdesc2step[slice][ito] < 0: ito = 1
			#print ifrom, ito
			if direction == 0:  colors[ self.__rotdesc2step[slice][ifrom] ] = copy.deepcopy( newcolors [ self.__rotdesc2step[slice][ito] ] )
			else:               colors[ self.__rotdesc2step[slice][ito] ] = copy.deepcopy( newcolors [ self.__rotdesc2step[slice][ifrom] ] )
			ito += 1
			ifrom += 1
   
		return True
		
	def __ComputeNextSimTime( self, currentTime ):
		# keyframes should happen each time a pixel hits a control point 
		if ( self.__step2Index == 2 and self.__step3Index == 3 ):
			return currentTime
			
		step2Time = self.__step2Times[ self.__step2Index + 1 ]
		step3Time = self.__step3Times[ self.__step3Index + 1 ]
		
		# 0 duration rotation does it all at once, then finishes
		if ( self.activeRotationTime <= 0.0 ):
			for i in range( len( self.__activeRotations ) ):
				self.__RotateTargetState( self.__rotdesc2step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
				self.__RotateTargetState( self.__rotdesc2step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
				self.__RotateTargetState( self.__rotdesc3step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
				self.__RotateTargetState( self.__rotdesc3step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
				self.__RotateTargetState( self.__rotdesc3step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
			self.__step2Index = 2
			self.__step3Index = 3
			return step2Time;
		
		if ( step2Time < step3Time ):
			if ( step2Time >= currentTime ):
				return currentTime
			else:
				for i in range( len( self.__activeRotations ) ):
					self.__RotateTargetState( self.__rotdesc2step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
				self.__step2Index = self.__step2Index + 1
				return step2Time
			
		if ( step3Time >= currentTime ):
			return currentTime
		for i in range( len( self.__activeRotations ) ):
			self.__RotateTargetState( self.__rotdesc3step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
		self.__step3Index = self.__step3Index + 1
		
		# This case handles the last step; don't want to add the sim time twice
		# (the last time associated w/ step2 + step3 is the same )
		if ( step3Time == step2Time ):
			for i in range( len( self.__activeRotations ) ):
				self.__RotateTargetState( self.__rotdesc2step[ self.__activeRotations[i][0] ], self.__activeRotations[i][1] )
			self.__step2Index = self.__step2Index + 1
		return step3Time
						
	# private methods below
	def __BlendColors( self, i, j, t ):
		srcColor = self.__RGBtoHSL( self.__targetcolors[src] )
		dstColor = self.__RGBtoHSL( self.__targetcolors[dest] )
			
		blendColor = [ 0.0, 0.0, 0.0 ]
			
		# for hue (blendColor[0]), pick shortest path
		if ( math.fabs( dstColor[0] - srcColor[0] ) > 0.5 ):
			if ( dstColor[0] < srcColor[0] ):
				dstColor[0] += 1.0
			else:
				srcColor[0] += 1.0
					
		blendColor[0] = srcColor[0] + ( dstColor[0] - srcColor[0] ) * t
		blendColor[1] = srcColor[1] + ( dstColor[1] - srcColor[1] ) * t
		blendColor[2] = srcColor[2] + ( dstColor[2] - srcColor[2] ) * t
			
		self.__colors[dest] = self.__HSLtoRGB( blendColor )
		
	def __RotateTargetState( self, indices, clockwise ):
		if ( indices[0] < 0 ):
			return
		initColors = self.__targetcolors[:]
		i = 1
		while indices[i] >= 0:
			if ( indices[i-1] == 9999 or indices[i] == 9999 ):
				i += 1
				continue
			if ( clockwise ):
				self.__targetcolors[ indices[i-1] ] = initColors[ indices[i] ][:]
			else:
				self.__targetcolors[ indices[i] ] = initColors[ indices[i-1] ][:]
			i += 1

	def __BlendTargetState( self, t, indices, clockwise ):
		i = 1;
		while indices[i] >= 0:
			if ( clockwise ):
				dest = indices[i]
				src = indices[i-1]
			else:
				dest = indices[i-1]
				src = indices[i]
			if ( dest == 9999 or src == 9999 ):
				i += 1
				continue
			   			
			# blend
			self.__colors[dest] = BlendColorsRGB( self.__targetcolors[src], self.__targetcolors[dest], t )
			i += 1
