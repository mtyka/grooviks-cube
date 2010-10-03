# Contains configuration data that can be re-read at any time for in-process tweaks


from GScript import GScriptLibrary;
from GScript import GScript
import ConfigParser
import string

class GroovikConfig:
	def __init__( self ):
		self.idlePulseDimFactor = 1.0
		self.lightBoardMap = []
		self.colorCorrection = [] 
		for i in range(54):
			self.lightBoardMap.append( i )
			self.colorCorrection.append( [ 1.0, 1.0, 1.0 ] )
		self.standardFaceColors = [ [0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0] ]
		self.calibrationColors = [ [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0] ]
		self.effectsLibrary = GScriptLibrary();
	
	def SetConfigFileName( self, fileName ):
		self.__configFileName = fileName 
		
	def LoadConfig( self ):
		# reload our effects library (victory dance, etc.)
		self.effectsLibrary.Load( "effects.library" )
		
		# Parse the file settings
		try:
			config = ConfigParser.RawConfigParser()
			config.read( self.__configFileName )
		
			self.standardFaceColors = self.__ParseColorArray( config, 'CubeState', 'standard_face_colors' )
			self.calibrationColors = self.__ParseColorArray( config, 'ModeCalibration', 'calibration_colors' )			
			self.lightBoardMap = self.__ParseIntArray( config, 'Display', 'physical_cube_pixel_mapping' )
			self.colorCorrection  = self.__ParseColorArray( config, 'Display', 'color_correction' )
			self.idlePulseDimFactor = config.getfloat( 'RotationState', 'idle_pulse_dim_factor' )	
		except:
			print "error parsing configuration file!"
			
		
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
		
		configfile = open( self.__configFileName, "wt" )
		config.write( configfile )
		configfile.close()
		
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