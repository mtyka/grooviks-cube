#-------------------------------------------------------------------------------
#
# state object used to strobe the cube (VICTORY)  
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import random
import copy


#cylindrical_map =  \
#[\
#[-1,-1,47,-1,-1,36,-1,-1,11],\
#[10,-1,50,46,-1,37,39,-1,14],\
#[ 9,53,49,45,38,40,42,17,13],\
#[12, 2,52,48,18,41,43,27,16],\
#[ 5, 1,51,19,21,44,28,30,15],\
#[ 8, 4, 0,20,22,24,29,31,33],\
#[ 7, 3,-1,23,25,-1,32,34,-1],\
#[-1, 6,-1,-1,26,-1,-1,35,-1]\
#]

#cylindrical_map =  \
#[\
#[-1,-1,47,-1,-1,27,-1,-1,11],\
#[10,-1,50,46,-1,28,30,-1,14],\
#[ 9,53,49,45,29,31,33,17,13],\
#[12,20,52,48, 0,32,34,36,16],\
#
#[23,19,51, 1, 3,35,37,39,15],\
#[26,22,18, 2, 4, 6,38,40,42],\
#[25,21,-1, 5, 7,-1,41,43,-1],\
#[-1,24,-1,-1, 8,-1,-1,44,-1]\
#]
cylindrical_map =  \
[\
[-1,-1,-1,-1,-1,47,-1,-1,-1,-1,-1,27,-1,-1,-1,-1,-1,11],\
[10,-1,-1,-1,50,-1,46,-1,-1,-1,28,-1,30,-1,-1,-1,14,-1],\
[-1, 9,-1,53,-1,49,-1,45,-1,29,-1,31,-1,33,-1,17,-1,13],\
[12,-1,20,-1,52,-1,48,-1, 0,-1,32,-1,34,-1,36,-1,16,-1],\
[-1,23,-1,19,-1,51,-1, 1,-1, 3,-1,35,-1,37,-1,39,-1,15],\
[26,-1,22,-1,18,-1, 2,-1, 4,-1, 6,-1,38,-1,40,-1,42,-1],\
[-1,25,-1,21,-1,-1,-1, 5,-1, 7,-1,-1,-1,41,-1,43,-1,-1],\
[-1,-1,24,-1,-1,-1,-1,-1, 8,-1,-1,-1,-1,-1,44,-1,-1,-1]\
]

class StateFire( StateBase ):
  def Start( self, currentTime, params, startingColors, faceColors, initialColorIndices ):
    print "Experimental.Start"
    print currentTime
    print params
    print startingColors
    print faceColors
    print initialColorIndices 
    print "-----------"
    
    duration = params[0]
    self.__duration = duration
    self.__starttime = currentTime
    self.__colors = copy.deepcopy( startingColors )

    self.__heatmap = copy.deepcopy( cylindrical_map );
    for y in range( 0, 8):
      for x in range( 0, 18 ):
        self.__heatmap[y][x] = 0
    self.__palette = []
    for i in range(0,60 ):
      self.__palette.append( [ 0,0,i/ 60.0] )
    for i in range( 60, 120):
      self.__palette.append( [ 0,(i- 60)/ 60.0,1] )
    for i in range(120, 256):
      self.__palette.append( [ (i-120)/136.0,1,1] )

    self.__colors = copy.deepcopy( startingColors )
    self.__step = 0

  def Update( self, currentTime ):
    print "Experimental.Update"
    print currentTime
    print self.__colors 
    print "-----------"
    # Simulate to the next control point / current time, which ever comes first
    # Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
   # simTime = self.__ComputeNextSimTime( currentTime )
   # if ( self.__strobeIndex >= self.__strobeControlPointCount - 1 ):
   #   return  [ self.__colors, simTime, True ]
    
    if (currentTime - self.__starttime) > self.__duration:
       return  [ self.__colors, (currentTime - self.__starttime), True ]
    
    output = [ [], currentTime, False ]
    i=0
   
#    local_output = []
#    for g in range(0,54):
#      local_output.append( [0,0,0] )
    
    for x in range( 0, 18 ):
      if random.randint(0,2) == 0:
        self.__heatmap[ 7][x] = 600
      else: 
        self.__heatmap[ 7][x] = 185

    for y in range( 0, 7):
      for x in range( 0, 18 ):
        self.__heatmap[y][x] = \
           self.__heatmap[ y+1][(x+17)%18 ] +  \
           self.__heatmap[ y+1][(x+18)%18 ] +  \
           self.__heatmap[ y+1][(x+18)%18 ] +  \
           self.__heatmap[ y+1][(x+18)%18 ] +  \
           self.__heatmap[ y+1][(x+19)%18 ]
        self.__heatmap[y][x] /= 8;

    for r,g,b in [(0,0,0), (0,0,0), (0,0,0),  (0,0,1), (0,1,0), (1,0,0) ]: 
      for j in range(0,9):
        output[0].append( [r*j/9.0, g*j/9.0, b*j/9.0] )
     #   print i
        i=i+1
    
    step=self.__step
    self.__step += 1
    for y in range( 0, 8):
      for x in range( 0, 18 ):
        pixelno = cylindrical_map[y+0][x]
        if pixelno >= 0:
          palette_color = self.__heatmap[y][x]
          if ( palette_color > 255): palette_color = 255; 
          output[0][pixelno] = self.__palette[ palette_color ] 
   
    return output 
    
#    step=self.__step
#    self.__step += 1
#    for y in range( 0, 8):
#      for x in range( 0, 18 ):
#        pixelno = cylindrical_map[y][x]
#        vertical_color_index = ((y+step)%15)-8;
#        if vertical_color_index < 0: vertical_color_index *= -1;
#        
#        angular_color_index = ((x+step)%17)-9;
#        if angular_color_index < 0: angular_color_index *= -1;
#        
#        angular_color_index2 = ((step/2-x)%17)-9;
#        if angular_color_index2 < 0: angular_color_index2 *= -1;
#
#        if pixelno >= 0:
#          output[0][pixelno] = [angular_color_index/9.0,angular_color_index2/9.0,vertical_color_index/8.0] 
#  
#    print "DONE!"
#    return output  
  
  def __ComputeNextSimTime( self, currentTime ):
    # keyframes should happen each time a pixel hits a control point
    if ( self.__strobeIndex >= self.__strobeControlPointCount - 1 ):
      return currentTime
    strobeTime = self.__strobeTimes[ self.__strobeIndex + 1 ]
    if ( strobeTime >= currentTime ):
      return currentTime
    self.__strobeIndex = self.__strobeIndex + 1
    return strobeTime

