#-------------------------------------------------------------------------------
#
# Class for maintaing state library and queries into it 
#
#-------------------------------------------------------------------------------
from groovikutils import *
from groovikconfig import *
from statebase import *
from staterotation import *
from hbclient import *
import copy


class MoveLibrary( StateRotation ):
	
	def __init__( self, library_file = "" ):
		super( MoveLibrary, self ).__init__()
		self.__state_hash = {}	
		if library_file != "":
			self.read_in_library( library_file )	


	def read_in_library( self, library_file ):
		print "Reading state library: ", library_file 
		
		data = open( library_file, "r" ).read()
		lines = data.split("\n")
		for i,l in enumerate(lines):
			tokens = l.split()
			# Add each entry into the hash
			try:		
				self.__state_hash[ tokens[0] ] = int( tokens[1] )
			except:
				print "Syntax error on line: ", i

 		#print self.__state_hash

	
	

	def PackCube( self, colors ):
		s=""
		for i in range(54): s+=str(int( colors[i][0]+2*colors[i][1]+4*colors[i][2] ) )
		return s
	
	def NormalizeCube( self, colors ):
		# find red middle facet and rotate such that middle facet is on first face
		if colors[4 ] == [0,0,1]:	## Opposite face
			pass
		elif colors[13] == [0,0,1]:	## Opposite face
			self.DoDirectRotation( colors, 3, 1 )
			self.DoDirectRotation( colors, 4, 1 )
			self.DoDirectRotation( colors, 5, 1 )
			self.DoDirectRotation( colors, 3, 1 )
			self.DoDirectRotation( colors, 4, 1 )
			self.DoDirectRotation( colors, 5, 1 )
		elif colors[22] == [0,0,1]:	## rotate once on z backwards
			self.DoDirectRotation( colors, 6, 0 )
			self.DoDirectRotation( colors, 7, 0 )
			self.DoDirectRotation( colors, 8, 0 )
		elif colors[31] == [0,0,1]: ## rotate once on z 
			self.DoDirectRotation( colors, 6, 1 )
			self.DoDirectRotation( colors, 7, 1 )
			self.DoDirectRotation( colors, 8, 1 )
		elif colors[40] == [0,0,1]: ## rotate once on y
			self.DoDirectRotation( colors, 3, 1 )
			self.DoDirectRotation( colors, 4, 1 )
			self.DoDirectRotation( colors, 5, 1 )
		elif colors[49] == [0,0,1]: ## rotate once on y backwards
			self.DoDirectRotation( colors, 3, 0 )
			self.DoDirectRotation( colors, 4, 0 )
			self.DoDirectRotation( colors, 5, 0 )
		else:
			print "IMPOSSIBLE!"

		## now put blue on 22
		if colors[22] == [1,0,0]:
			pass
		elif colors[49] == [1,0,0]: ## one x rotation
			self.DoDirectRotation( colors, 0, 1 )
			self.DoDirectRotation( colors, 1, 1 )
			self.DoDirectRotation( colors, 2, 1 )
		elif colors[40] == [1,0,0]: ## one reverse x rotation
			self.DoDirectRotation( colors, 0, 0 )
			self.DoDirectRotation( colors, 1, 0 )
			self.DoDirectRotation( colors, 2, 0 )
		elif colors[31] == [1,0,0]: ## two full x rotations
			self.DoDirectRotation( colors, 0, 0 )
			self.DoDirectRotation( colors, 1, 0 )
			self.DoDirectRotation( colors, 2, 0 )
			self.DoDirectRotation( colors, 0, 0 )
			self.DoDirectRotation( colors, 1, 0 )
			self.DoDirectRotation( colors, 2, 0 )
		else:
			print "EQALLYIMPOSSIBLE!"
	
	
		
	def Recursive_make_all_single_moves( self, start_state, state_hash, maxdepth, depth = 0, add_current = False ):
		if add_current: 
			curstate =	copy.deepcopy( start_state )
			self.NormalizeCube( curstate )
			packed_state = self.PackCube( curstate ) 
			state_hash[ packed_state ] = depth 

		if depth == maxdepth: return
		for a in range(18):
			curstate =	copy.deepcopy( start_state )
			self.DoDirectRotation( curstate, a/2 , a%2 )
			self.NormalizeCube( curstate )
			self.Recursive_make_all_single_moves( curstate, state_hash, maxdepth, depth + 1) 
			packed_state = self.PackCube( curstate ) 
			if packed_state in state_hash:
			  if state_hash[ packed_state ] > (depth + 1):
				  state_hash[ packed_state ] = depth + 1
			else: state_hash[ packed_state ] = depth + 1


	def AnalysePosition( self, query_colors ):
		try:
			current_position = copy.deepcopy( query_colors )
			self.NormalizeCube( current_position )
			packed = self.PackCube( current_position )
			print packed
			moves_from_solved = int(self.__state_hash[ packed ])
			print "Moves from solved: ", moves_from_solved
			return moves_from_solved
		except:
		  ## Not in library - means we dont have data on how far this state is
			return -1; 	
			
	def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
		self.__targetcolors = copy.deepcopy( startingColors )
		
	def Update( self, currentTime ):
		moves_to_solved = self.AnalysePosition( self.__targetcolors );
		print "Moves To Solved: ", moves_to_solved
		push_message( moves_to_solved , "movesfromsolved")
		
		# Simulate to the next control point / current time, which ever comes first
		# Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
		output = [ self.__targetcolors, currentTime, True ]
		
		return output	

