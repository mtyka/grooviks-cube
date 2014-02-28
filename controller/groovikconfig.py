# Contains configuration data that can be re-read at any time for in-process tweaks

from GScript import GScriptLibrary;
from GScript import GScript
from hbclient import *
import ConfigParser
import json
import string


class GroovikConfig:
	def __init__( self ):
		self.idlePulseDimFactor = 1.0
		self.lightBoardMap = []
		self.colorCorrection = []
		self.kioskSettings = {}
		self.leaderboard = []
		for i in range(54):
			self.lightBoardMap.append( i )
			self.colorCorrection.append( [ 1.0, 1.0, 1.0 ] )
		self.standardFaceColors = [ [0.0, 1.0, 0.0], [1.0, 0.0, 0.0],
									[1.0, 0.0, 1.0], [0.0, 0.0, 1.0],
									[0.0, 1.0, 1.0], [1.0, 1.0, 1.0],
									[0.5, 0.5, 0.5]]
		self.calibrationColors = [ [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0] ]
		self.effectsLibrary = GScriptLibrary();

	def SetConfigFileName( self, fileName ):
		self.__configFileName = fileName

	def LoadConfig( self ):
		# reload our effects library (victory dance, etc.)
		self.effectsLibrary.Load( "effects.library" )

		# Parse the file settings
		# you want this to break if it's bad, hence try,except commented out.
		# try:
		config = ConfigParser.RawConfigParser()
		config.read( self.__configFileName )

		#self.standardFaceColors = self.__ParseColorArray( config, 'CubeState', 'standard_face_colors' )
		self.calibrationColors = self.__ParseColorArray( config, 'ModeCalibration', 'calibration_colors' )
		self.lightBoardMap = self.__ParseIntArray( config, 'Display', 'physical_cube_pixel_mapping' )
		self.colorCorrection  = self.__ParseColorArray( config, 'Display', 'color_correction' )
		self.kioskSettings = self.__ParseDictionary(config, 'KioskSettings', 'settings')
		self.leaderboard = self.__ParseArrayFromDictionary(config, 'Leaderboard', 'board', 'board')
		self.idlePulseDimFactor = config.getfloat( 'RotationState', 'idle_pulse_dim_factor' )
		# except:
 		#	print "error parsing configuration file!"


	def SaveConfig( self ):
		# Config parser kind of sucks. It doesn't allow you to control formatting or
		# order of output of sections or options. So I have to do a little string formatting
		# myself to get something reasonably parseable + modifyable in a text mode

		config = ConfigParser.RawConfigParser()

		config.add_section( 'Display' )
		self.__outputArray( config, 'Display', 'color_correction', self.colorCorrection )
		self.__outputArray( config, 'Display', 'physical_cube_pixel_mapping', self.lightBoardMap )

		config.add_section( 'RotationState' )
		config.set( 'RotationState', 'idle_pulse_dim_factor', self.idlePulseDimFactor )

		config.add_section( 'CubeState' )
		self.__outputArray( config, 'CubeState', 'standard_face_colors', self.standardFaceColors )

		config.add_section( 'ModeCalibration' )
		self.__outputArray( config, 'ModeCalibration', 'calibration_colors', self.calibrationColors )

		config.add_section( 'KioskSettings' )
		config.set('KioskSettings', 'settings', json.dumps(self.kioskSettings))

		config.add_section( 'Leaderboard' )
		config.set('Leaderboard', 'board', json.dumps({'board':self.leaderboard}))

		print "Saving to " + self.__configFileName
		configfile = open( self.__configFileName, "w")
		config.write( configfile )
		configfile.close()

	def getLeaderboard(self):
		print json.dumps({'sub': 'leaderboard', 'set':self.leaderboard})
		push_message(json.dumps({'sub': 'leaderboard', 'set':self.leaderboard}), 'info')

	def addLeaderboardEntry(self, time, moves):
		print type(self.leaderboard)
		self.leaderboard.append({'time': time, 'moves':moves})

	def clearLeaderboard(self):
		self.leaderboard = [];

	def getSettings(self):
		print "current settings: " + json.dumps(self.kioskSettings)
		push_message(json.dumps(self.kioskSettings) + "", 'settings')

	def setSettings(self, newValues):
		print "sent settings: " + str(newValues)
		self.kioskSettings = newValues.copy()
		print "new kiosk settings: " + str(self.kioskSettings)
		push_message(json.dumps(self.kioskSettings) + "", 'settings')
		self.SaveConfig()

	def __ParseIntArray( self, configParser, section, option ):
		parsedString = configParser.get( section, option )
		parsedString = string.join( parsedString.split(), "" )
		parsedString = parsedString.lstrip('[').rstrip(']')
		output = [int(x) for x in parsedString.split(',')]
		return output

	def __ParseFloatArrayString( self, parsedString ):
		parsedString = string.join( parsedString.split(), "" )
		parsedString = parsedString.lstrip('[').rstrip(']')
		output = [float(x) for x in parsedString.split(',')]
		return output

	def __ParseFloatArray( self, configParser, section, option ):
		parsedString = configParser.get( section, option )
		return __ParseFloatArrayString( parsedString )

	def __ParseColorArray( self, configParser, section, option ):
		colorStringArray = configParser.get( section, option )

		# Strip enclosing [] and all internal whitespace
		colorStringArray = string.join( colorStringArray.split(), "" )
		colorStringArray = colorStringArray.lstrip('[').rstrip(']')
		colors = []
		for colorString in colorStringArray.split('],['):
			color = self.__ParseFloatArrayString( colorString );
			colors.append( color )
		return colors

	def __ParseArrayFromDictionary(self, configParser, section, option, key):
		obj = configParser.get( section, option ).replace("'", "\"").replace("\n","")
		obj = json.loads(obj)
		arr = obj[key]
		print "array: " + str(arr)
		return arr

	def __ParseDictionary(self, configParser, section, option):
		obj = configParser.get( section, option ).replace("'", "\"").replace("\n","")
		print "dict: " + str(obj)
		tmpRet = json.loads(obj)
		ret = {}
		for key in tmpRet.keys():
			ret[str(key)] = str(tmpRet[key])
		return ret

	def __outputArray( self, configParser, section, option, array ):
		arrayString = '\n[\n'
		for i in range( len(array) ):
			arrayString += str( array[i] )
			if ( i < (len(array)-1) ):
				arrayString += ','
			arrayString += '\n'
		arrayString += ']'
		configParser.set( section, option, arrayString )

groovikConfig = GroovikConfig()