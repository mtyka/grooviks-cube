#
# Groovik state object
#
# Groovik's cube has 54 colors, arranged (at the moment) in this fashion:
#  x = 1        x = -1         y = 1         y = -1        z = 1       z = -1
# Z           Z              Z             Z             Y            Y
# ^           ^              ^             ^             ^            ^
# |6 7 8      |15 16 17      |24 25 26     |33 34 35     |42 43 44    |51 52 53
# |3 4 5      |12 13 14      |21 22 23     |30 31 32     |39 40 41    |48 49 50
# |0 1 2      |9  10 11      |18 19 20     |27 28 29     |36 37 38    |45 46 47
#  ------> Y   --------> -Y   -------> -X   --------> X   -------->X   --------> -X

import sys
import math

# Set devel mode or not
dev_mode = 1

class Enum(set):
    '''Checked enumerations, from http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python'''

    def __init__(self, initStr):
    	'''Build an enum from a string containing all of the states'''
    	set.__init__(self, initStr.split())

    def __getattr__(self, name):
    	'''
    	Treat any attribute lookup for a name in the init list as an
    	enumeration constant, and anything else as an error
    	'''
        if name in self:
            return name
        raise AttributeError

#-------------------------------------------------------------------------------
# Cube states
#-------------------------------------------------------------------------------
class CubeState:
	UNKNOWN = -1
	IDLE = 0             # Note: This state should never be queued directly. The system will do it for you
	IDLEPULSE = 1
	ROTATING_OLDSTYLE = 2
	STROBE = 3
	FADE = 4
	SPIRALFADE = 5
	DELAY = 6
	ROTATING = 7
	SWITCH_MODE = 8
	FIREMODE = 9
	TETRISMODE = 10
	MOVELIBRARY=11
#-------------------------------------------------------------------------------
# Game state:  These states define which clients are allowed to interact with
# the cube game, and what actions they are allowed to take.
#
# See http://code.google.com/p/grooviks-cube/wiki/PacsciStateMachine#Global_State
# for more information.
#-------------------------------------------------------------------------------
ClientState = Enum('IDLE HOME SING MULT VICT QUEUED')

ClientCommand = Enum('WAKE QUIT START_1P START_3P JOIN_3P SELECT_DIFFICULTY')

GameState = Enum('UNBOUND SINGLE SINGLE_INVITE MULTIPLE VICTORY')

#-------------------------------------------------------------------------------
# Cube modes
#-------------------------------------------------------------------------------
class CubeMode:
	UNKNOWN = -1
	NORMAL = 0
	MATCH3 = 0.1
	SYMMETRIC = 0.2
	PARTIAL = 0.3
	CALIBRATION = 1
	LIGHT_BOARD_CONFIGURATION = 2
	SCREENSAVER = 3
	CUBE_MODE_COUNT = 4 # make sure this is last

#-------------------------------------------------------------------------------
# Cube input types
#-------------------------------------------------------------------------------
class CubeInput:
	ROTATION = 0     # Requires input parameter of the form [ [ rotation type (0-8), clockwise (True or False) ], ... ] (used to queue multiple simultaneous rotations)
	SWITCH_MODE = 1  # Requires input parameter of the form < cube mode to switch to (see CubeMode) >
	FACE_CLICK = 2 # Requires input parameter of the form < logicalPixelID (see lightboard.py) >
	COLOR_CAL = 3 # Requires input parameter of the form [ Pixel to change calib for, ( R G B ) ], where R G B are from 0 to 1


#-------------------------------------------------------------------------------
# Color blending helper methods
#-------------------------------------------------------------------------------
def RGBtoHSL( rgb ):
	maxRGB = max( max( rgb[0], rgb[1] ), rgb[2] )
	minRGB = min( min( rgb[0], rgb[1] ), rgb[2] )
	hsl = [ 0.0, 0.0, 0.0 ]
	hsl[2] = ( maxRGB + minRGB ) / 2.0
	if ( maxRGB == minRGB ):
		hsl[0] = hsl[1] = 0.0
		return hsl
	deltaRGB = maxRGB - minRGB
	if ( hsl[2] < 0.5 ):
		hsl[1] = deltaRGB / ( maxRGB + minRGB )
	else:
		hsl[1] = deltaRGB / ( 2.0 - maxRGB - minRGB )
	if ( rgb[0] == maxRGB ):
		hsl[0] = ( rgb[1] - rgb[2] ) / deltaRGB
		if ( hsl[0] < 0.0 ):
			hsl[0] += 6.0
	elif ( rgb[1] == maxRGB ):
		hsl[0] = ( 2.0 + ( rgb[2] - rgb[0] ) / deltaRGB )
	else:
		hsl[0] = ( 4.0 + ( rgb[0] - rgb[1] ) / deltaRGB )
	hsl[0] /= 6.0
	return hsl;

def HSLComponent( temp1, temp2, temp3 ):
	temp3 = math.fmod( temp3 + 1.0, 1.0 )
	if ( temp3 < ( 1.0 / 6.0 ) ):
		return temp1 + ( temp2 - temp1 ) * 6.0 * temp3
	elif ( temp3 < ( 1.0 / 2.0 ) ):
		return temp2
	elif ( temp3 < ( 2.0 / 3.0 ) ):
		return temp1 + ( temp2 - temp1 ) * ( ( 2.0 / 3.0 ) - temp3 ) * 6.0
	else:
		return temp1

def HSLtoRGB( hsl ):
	rgb = [ 0.0, 0.0, 0.0 ]
	if ( hsl[1] == 0.0 ):
		rgb[0] = rgb[1] = rgb[2] = hsl[2];
		return rgb
	if ( hsl[2] < 0.5 ):
		temp2 = hsl[2] * ( 1.0 + hsl[1] )
	else:
		temp2 = hsl[2] + hsl[1] - hsl[2] * hsl[1]
	temp1 = 2.0 * hsl[2] - temp2
	rgb[0] = HSLComponent( temp1, temp2, hsl[0] + 1.0 / 3.0 )
	rgb[1] = HSLComponent( temp1, temp2, hsl[0] )
	rgb[2] = HSLComponent( temp1, temp2, hsl[0] - 1.0 / 3.0 )
	return rgb

def BlendColorsHSL( inSrcColor, inDstColor, t ):
	srcColor = RGBtoHSL( inSrcColor )
	dstColor = RGBtoHSL( inDstColor )
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
	return HSLtoRGB( blendColor )

def BlendColorsRGB( srcColor, dstColor, t ):
	t *= t * t
	blendColor = [ 0.0, 0.0, 0.0 ]
	blendColor[0] = srcColor[0] + ( dstColor[0] - srcColor[0] ) * t
	blendColor[1] = srcColor[1] + ( dstColor[1] - srcColor[1] ) * t
	blendColor[2] = srcColor[2] + ( dstColor[2] - srcColor[2] ) * t
	return blendColor;


#-------------------------------------------------------------------------------
# Simulation timestep, be careful to not reduce this below what the lightboards can handle!
#-------------------------------------------------------------------------------
TIMESTEP = 0.3

