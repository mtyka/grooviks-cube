#-------------------------------------------------------------------------------
#
# state object used to strobe the cube (VICTORY)  
#
#-------------------------------------------------------------------------------
from groovikutils import *
from statebase import *
import random
import copy

tetris_map = [ \
[ -1,-1,-1,-1,-1,-1,11,10, 9,20,19,18,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,14,13,12,23,22,21,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,17,16,15,26,25,24,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,27,30,33,36,39,42,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,28,31,34,37,40,42,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,29,32,35,38,41,44,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ 47,46,45, 0, 3, 6,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ 50,49,48, 1, 4, 7,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ 53,52,51, 2, 5, 8,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ 20,19,18,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ 23,22,21,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ 26,25,24,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ],\
[ -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ]\
]



class StateTetris( StateBase ):
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
    self.__step = 0

    self.__current_output = []
    for r,g,b in [(0,0,0), (0,0,0), (0,0,0),  (0,0,0), (0,0,0), (0,0,0) ]: 
      for j in range(0,9):
        self.__current_output.append( [0.0,0.0,0.0] )

    self.__current_color = [1,0,0]
    self.__current_shape = [[0,0]]
    #self.__current_shape = [[0,0],[0,1]]
    self.__current_position = []

  def checkPosition( self, output, position ):
    is_free = True
    for px,py in self.__current_shape:
      pixel_id = tetris_map[ position[0] + px][ position[1] + py]
      # have we hit an edge ?
      if pixel_id < 0: 
        print "Edge reached", position[0], px, position[1], py
        is_free = False
        break  
      # have we hit another piece ?
      if output[0][ pixel_id ] != [0,0,0] :
        print "Pixel reached", position[0], px, position[1], py, output[0][ pixel_id ]
        is_free = False
        break
    return is_free

  def drawPosition( self, output, position, color ):
    for px,py in self.__current_shape:
      pixel_id = tetris_map[ position[0] + px][ position[1] + py]
      output[0][ pixel_id ] = color

  def Update( self, currentTime ):
    #print "Experimental.Update"
    #print currentTime
    #print self.__colors 
    #print "-----------"
    # Simulate to the next control point / current time, which ever comes first
    # Update returns a list; first element is a list containing colors, second element is time, 3rd element is whether the state is done
   # simTime = self.__ComputeNextSimTime( currentTime )
   # if ( self.__strobeIndex >= self.__strobeControlPointCount - 1 ):
   #   return  [ self.__colors, simTime, True ]
   
    if (currentTime - self.__starttime) > self.__duration:
       return  [ self.__colors, (currentTime - self.__starttime), True ]

    output = [ self.__current_output, currentTime, False ]
    
    step=self.__step
    self.__step += 1
    
    if self.__current_position == []:
      #print "MAKE NEW PIECE!"
      ## set a position
      ri = random.randint(0,2)
      if ri == 0: self.__current_position = [0,6]
      if ri == 1: self.__current_position = [3,3]
      if ri == 2: self.__current_position = [6,0]
    
      ri = random.randint(0,11)
      if ri == 0:  self.__current_color = [1.0,0.0,0.0]
      if ri == 1:  self.__current_color = [0.0,1.0,0.0]
      if ri == 2:  self.__current_color = [0.0,0.0,1.0]
      if ri == 3:  self.__current_color = [1.0,1.0,0.0]
      if ri == 4:  self.__current_color = [0.0,1.0,1.0]
      if ri == 5:  self.__current_color = [1.0,0.0,1.0]
      if ri == 6:  self.__current_color = [0.6,0.0,0.0]
      if ri == 7:  self.__current_color = [0.0,0.6,0.0]
      if ri == 8:  self.__current_color = [0.0,0.0,0.6]
      if ri == 9:  self.__current_color = [0.6,1.0,0.0]
      if ri == 10: self.__current_color = [0.0,0.6,1.0]
      if ri == 11: self.__current_color = [0.6,0.0,1.0]
      
      ri = random.randint(0,2)
      if ri == 0: self.__current_shape = [[0,0]]
      if ri == 1: self.__current_shape = [[0,0], [0,1]]
      if ri == 2: self.__current_shape = [[0,0], [1,0]]

    
    ## undraw the piece
    old_position = copy.deepcopy(self.__current_position)
    #print old_position, self.__current_position
    

    self.drawPosition( output, self.__current_position, [0.0, 0.0, 0.0] )
    
    is_free = self.checkPosition( output, self.__current_position )
    if not is_free:
      #print "Tetris is done!"
      return output

   
    ## move the piece tentatively
    dx = random.randint(0,1)
    dy = 1 - dx;
    self.__current_position[0] += dx
    self.__current_position[1] += dy
    
    is_free = self.checkPosition( output, self.__current_position )
    if not is_free:
      #print "NOT FREE AFTER MOVE1"
      self.__current_position = copy.deepcopy(old_position) 
      
      # Now try the other way to go

      swap = dx
      dx = dy
      dy = swap
      self.__current_position[0] += dx
      self.__current_position[1] += dy
  
      # Is it free now ?
      is_free = self.checkPosition( output, self.__current_position )
      if not is_free:
        #print "NOT FREE AFTER MOVE2"
        self.__current_position = copy.deepcopy(old_position) 


    #print "Final: " , old_position, self.__current_position
    self.drawPosition( output, self.__current_position, self.__current_color  )
    
    ## If we were stuck then make a new piece
    if not is_free:
      #print "MAKE: Is not free - we need to reset and make a  new piece"
      self.__current_position = [] 
     

#      self.__current_position = old_position 
#      swap = dx
#      dx = dy
#      dy = swap
#      self.__current_position[0] += dx
#      self.__current_position[1] += dy
#      is_free = True
#      for px,py in self.__current_shape:
#        # have we hit an edge ?
#        if tetris_map[ self.__current_position[0] + px][ self.__current_position[1] + py] < 0: 
#          if_free = False
#          break  
#        # have we hit another piece ?
#        if output[0][ tetris_map[ self.__current_position[0] + px][ self.__current_position[1] + py] ] != [0,0,0] :
#          is_free = False
#          break
#    
#    # if still not free, revert position and conclude we're done. leave the piece where it is and generate a new position
#    if not is_free:
#      self.__current_position = old_position
#
#
#    ## draw the piece
#    for px,py in self.__current_shape:
#      print self.__current_position[0],px
#      print self.__current_position[1],py
#
#      the_index = tetris_map[ self.__current_position[0] + px][self.__current_position[1] + py]
#      print the_index
#      if the_index < 0:
#        is_free = False
#        print "HOW IS THIS POSSIBLE !?"
#        break
#      output[0][ the_index ] = self.__current_color 
#  
#    ## if the piece is stuck, then indicate we must generate a new piece new round
#    if not is_free:
#      self.__current_position = [] 

#    if step > 0:
#      color = [1,0,0]
#      for h in [50,49]: output[0][h] = color;
   
    return output 
    
  
  def __ComputeNextSimTime( self, currentTime ):
    return currentTime
    # keyframes should happen each time a pixel hits a control point
    if ( self.__strobeIndex >= self.__strobeControlPointCount - 1 ):
      return currentTime
    strobeTime = self.__strobeTimes[ self.__strobeIndex + 1 ]
    if ( strobeTime >= currentTime ):
      return currentTime
    self.__strobeIndex = self.__strobeIndex + 1
    return strobeTime

