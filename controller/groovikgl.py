# Groovik renderer in python

import math
import time
import copy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from groovikutils import *

class GroovikGLRenderer( ):		    
	def __init__( self ):
		self.__drawAxes = False
		self.__drawColorTransitions = False
		self.__queuedKeyframes = []
		self.__currentKeyframes = []
		self.__startKeyframes = []
	
	def ToggleDrawAxes( self ):
		self.__drawAxes = not self.__drawAxes

	def ToggleDrawColorTransitions( self ):
		self.__drawColorTransitions = not self.__drawColorTransitions
		
	def QueueKeyframes( self, keyframes ):
		for keyframe in keyframes:
			self.__queuedKeyframes.append( keyframe )
		
	def Draw( self, width, height, altitude, azimuth, distance, faceColors ):
		glViewport( 0, 0, width, height )
		
		# set viewing projection
		aspectRatio = float( height ) / float( width )
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glFrustum(-0.5, 0.5, -0.5 * aspectRatio, 0.5 * aspectRatio, 1.0, 50.0)

		# position viewer
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		cx = distance * math.cos( azimuth ) * math.sin( altitude )
		cy = distance * math.sin( azimuth ) * math.sin( altitude )
		cz = distance * math.cos( altitude )	
		gluLookAt( cx, cy, cz, 0, 0, 0, 0, 0, 1 )

		# other state
		glEnable( GL_CULL_FACE )
		glFrontFace( GL_CCW )
		glCullFace( GL_BACK )

		glEnable(GL_DEPTH_TEST)
		
		# clear color and depth buffers
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		if ( self.__drawAxes == True ):
			glBegin(GL_LINES)
			glColor3f( 1, 0, 0 )
			glVertex3f( 0, 0, 0 )
			glColor3f( 1, 0, 0 )
			glVertex3f( 5, 0, 0 )
			
			glColor3f( 1, 1, 0 )
			glVertex3f( 0, 0, 0 )
			glColor3f( 0, 1, 0 )
			glVertex3f( 0, 5, 0 )
			
			glColor3f( 0, 0, 1 )
			glVertex3f( 0, 0, 0 )
			glColor3f( 0, 0, 1 )
			glVertex3f( 0, 0, 5 )
			glEnd()
			
		glBegin(GL_QUADS)
		
		# Lerp the keyframes
		currentTime = time.clock()

		# Logic here is such:
		# We have a 'current' keyframe list we are currently processing, which has one more more keyframes in it.
		# Here, we take all queued keyframes and append them to the end of the 'current' keyframe list, 
		# emptying the queued keyframe list.
		# We also keep track of the time at which the first keyframe in the current list was started
		# Therefore if there is nothing in the current list before we do this operation, 
		# we must update the start time of the first keyframe to be the current time
		if ( len(self.__queuedKeyframes) > 0 ):
			if ( len(self.__currentKeyframes) == 0 ): 
				self.__currentKeyframes = copy.deepcopy( self.__queuedKeyframes )
				self.__currentKeyframeStartTime = currentTime
			else:
				for keyframe in self.__queuedKeyframes:
					self.__currentKeyframes.append( copy.deepcopy( keyframe ) )	
			self.__queuedKeyframes = []
		
		if ( len( self.__currentKeyframes ) != 0 ):	
			# If we have keyframes in our list, then we must discover which keyframes surround the current time
			# This loop will iterate over all keyframes to compute index, the index of the first
			# keyframe after the current time. We will lerp between keyframe[index-1] and keyframe[index]
			deltaTime = currentTime - self.__currentKeyframeStartTime
			index = 0
			t = 0.0
			for keyframe in self.__currentKeyframes:
				duration = keyframe[0] * 0.004 # Convert back into seconds
				if ( duration > deltaTime ):
					t = deltaTime / duration
					break
				deltaTime = deltaTime - duration
				index = index + 1
			
			# This is where the keyframe lerp happens. 
			colors = []
			keyframeCount = len( self.__currentKeyframes )
			if ( index < keyframeCount ):		
				i = 0
				while ( i < len( self.__currentKeyframes[index][1] ) ):
					if ( index > 0 ):
						# If we're in the middle of the list, then we lerp between one keyframe and the next						
						blendColor = BlendColorsRGB( self.__currentKeyframes[index-1][1][i], self.__currentKeyframes[index][1][i], t )					
					else:
						# If we're at the start of the list, we lerp from the previous cube state to the first keyframe
						blendColor = BlendColorsRGB( self.__startKeyframes[i], self.__currentKeyframes[index][1][i], t )	
					colors.append( blendColor )
					i = i + 1
			else:
				# In this case, time has passed all keyframes. We delete the current keyframe list
				# and cache off the current keyframes in __startKeyframes to lerp against the next time
				# we get keyframes, and also to use when there are no keyframes
				colors = self.__currentKeyframes[ keyframeCount - 1 ][1]
				self.__startKeyframes = copy.deepcopy( colors )
				self.__currentKeyframes = []
		else:
			# In this case, there are no current keyframes. The cube is idle.
			# Just render the state we ended up with the last time we had keyframes
			# This works because we always start the process with a keyframe.
			colors = self.__startKeyframes
			
		# update the LED boards
		crossAxis = [ [1, 2], [0, 2], [0, 1] ]
		invertAxis = [ [False, False], [True, False], [True, False], [False, False], [False, False], [True, False] ]
		gapSize = 0.08
		p = [ 0.0, 0.0, 0.0 ]
		d = [ 0.0, 0.0, 0.0 ]
		g = [ 0.0, 0.0, 0.0 ]

		for i in range( 0, 6 ):
			axis = i / 2;
			p[axis] = 3.0
			if ( i & 1 ):
				p[axis] *= -1.0
			d[axis] = 0.0

			a0 = crossAxis[ axis ][ 0 ]
			a1 = crossAxis[ axis ][ 1 ]
			s0 = 1.0
			s1 = 1.0
			if ( invertAxis[ i ][ 0 ] ):
				s0 *= -1.0
			if ( invertAxis[ i ][ 1 ] ):
				s1 *= -1.0		
			d[a0] = ( 2.0 - 2.0 * gapSize ) * s0
			d[a1] = ( 2.0 - 2.0 * gapSize ) * s1
			g[a0] = gapSize * s0
			g[a1] = gapSize * s1
			p[a1] = -3.0 * s1 + g[a1]
			for j in range( 0, 3 ):
				p[a0] = -3.0 * s0 + g[a0]
				for k in range( 0, 3 ):
					ndx = i*9 + j*3 + k
					glColor3f( colors[ ndx ][2], colors[ ndx ][1], colors[ ndx ][0] )
					glVertex3f( p[0], p[1], p[2] )
					p[ a0 ] += d[ a0 ]

					glColor3f( colors[ ndx ][2], colors[ ndx ][1], colors[ ndx ][0] )
					glVertex3f( p[0], p[1], p[2] );
					p[ a1 ] += d[ a1 ];

					glColor3f( colors[ ndx ][2], colors[ ndx ][1], colors[ ndx ][0] )
					glVertex3f( p[0], p[1], p[2] );
					p[ a0 ] -= d[ a0 ];

					glColor3f( colors[ ndx ][2], colors[ ndx ][1], colors[ ndx ][0] )
					glVertex3f( p[0], p[1], p[2] );
					p[ a1 ] -= d[ a1 ];
					p[ a0 ] += d[ a0 ] + 2.0 * g[ a0 ];			    
				p[ a1 ] += d[ a1 ] + 2.0 * g[ a1 ];
		glEnd()
		
		self.__DrawColorTransitions( width, height, faceColors )

	def __DrawColorTransition( self, rect, viewportWidth, viewportHeight, start, end ):
		glEnable( GL_CULL_FACE )
		glFrontFace( GL_CCW )
		glCullFace( GL_BACK )

		# set the projection matrix to a normal frustum with a max depth of 50
		glMatrixMode( GL_PROJECTION )
		glLoadIdentity()
		glOrtho( 0.0, viewportWidth, viewportHeight, 0.0, 0.0, 1.0 )

		# reset view matrix
		glMatrixMode( GL_MODELVIEW )
		glLoadIdentity()

		glBegin(GL_QUADS)
		dx = rect[2] / 255.0
		x = float( rect[0] )
		c = [ 0.0, 0.0, 0.0 ]
		for i in range( 0, 256 ):
			c = BlendColorsRGB( start, end, float( i ) / 255.0 )
			glColor3f( c[0], c[1], c[2] )
			glVertex3f( x, float( rect[1] + rect[3] ), 0.0 )
			glColor3f( c[0], c[1], c[2] )
			glVertex3f( x + dx, float( rect[1] + rect[3] ), 0.0 )
			glColor3f( c[0], c[1], c[2] )
			glVertex3f( x + dx, float( rect[1] ), 0.0 )
			glColor3f( c[0], c[1], c[2] )
			glVertex3f( x, float( rect[1] ), 0.0 )
			x += dx
		glEnd()

	def __DrawColorTransitions( self, width, height, faceColors ):
		if ( self.__drawColorTransitions == False ):
			return
		r = [ 10, height - 30, 255, 20 ]
		faceColorCount = len(faceColors)
		for i in range( 0, faceColorCount-1 ):
			for j in range( i+1, faceColorCount ): 
				self.__DrawColorTransition( r, width, height, faceColors[i], faceColors[j] )
				r[0] = r[0] + r[2] + 10
				if ( r[0] + 255 > width ):
					r[0] = 10
					r[1] -= r[3] + 10

