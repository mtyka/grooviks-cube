import sys
import random
import copy

class GScriptSubgroup:
	NORMAL = 0
	RANDOM = 1
	REPEAT = 2
	
class GScript:
	def Load(self, fileName):
		self.moves = []
		subgroupCountRemaining = 0
		subgroupType = GScriptSubgroup.NORMAL
		subgroupApplyCount = 0
		subgroup = []
		for line in file(fileName):
			# Support for repeat/random. Special keywords in the script
			parsedLine = eval( line )
			if ( subgroupType == GScriptSubgroup.NORMAL ):
				if ( len( parsedLine ) == 3 ):
					if ( parsedLine[0] is 'random' ):
						subgroupType = GScriptSubgroup.RANDOM
						subgroupCountRemaining = parsedLine[1]
						subgroupApplyCount = parsedLine[2]
						subgroup = []
						continue
					elif ( parsedLine[0] is 'repeat' ):
						subgroupType = GScriptSubgroup.REPEAT
						subgroupCountRemaining = parsedLine[1]
						subgroupApplyCount = parsedLine[2]
						subgroup = []
						continue	
				self.moves.append( parsedLine )
				continue
			else:
				subgroup.append( parsedLine )
				subgroupCountRemaining = subgroupCountRemaining - 1
				if ( subgroupCountRemaining > 0 ):
					continue
				if ( subgroupType is GScriptSubgroup.REPEAT ):
					for i in range( subgroupApplyCount ):
						for subgroupLine in subgroup:
							self.moves.append( copy.deepcopy( subgroupLine ) )
				elif ( subgroupType is GScriptSubgroup.RANDOM ):
					for i in range( subgroupApplyCount ):
						j = random.randint( 0, len( subgroup ) - 1 )
						self.moves.append( copy.deepcopy( subgroup[j] ) )
				subgroupType = GScriptSubgroup.NORMAL
				
	def CreateRandom(self, depth, time):
		self.moves = [];
		for i in range(depth):
			# note... if we want to add more commands that this script can hit, we'll need to update this randint as well
			rot = random.randint( 0, 8 )
			clockwise = ( random.randint( 0, 1 ) == 1 )
			# NOTE: The '2' is the enum for rotation
			self.moves.append([2, rot, clockwise, time]);

	def ForceQueue(self, cube):
		for move in self.moves:
			cube.ForceQueueCubeState( move )

class GScriptLibrary:
	def Load(self, fileName):
		self.scripts = [];
		self.scriptMap = {};
		for line in file(fileName):
			l = eval(line);
			NAME = l[1];
			ID = l[0];
			script = GScript();
			script.Load(NAME);
			self.scripts.append(script);
			self.scriptMap[ID] = script;

	def ForceQueueByID(self, ID, cube):
		script = self.scriptMap[ID];
		script.ForceQueue(cube);

	def ForceQueueByIndex(self, index, cube):
		script = self.scripts[ID];
		script.ForceQueue(cube);

	def ForceQueueByRandom(self, cube):
		index = random.randint( 0, len(self.scripts) -1 )
		script = self.scripts[index];
		script.ForceQueue(cube);


