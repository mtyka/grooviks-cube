# Groovik renderer in python

import wx
import sys
import math
import time
import fileinput
import groovik
import copy
from groovikutils import *
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from GScript import GScriptLibrary;
from GScript import GScript
from glog import GLog;
from groovikconfig import *
from groovikgl import *

class GroovikCanvas(glcanvas.GLCanvas):
	def __init__(self, parent):
		glcanvas.GLCanvas.__init__(self, parent, -1)

		# initial mouse position
		self.lastx = 0
		self.lasty = 0
		
		# initial altitude and azimuth
		self.altitude = 3.14 / 6.0
		self.azimuth = -3.0 * 3.14 / 4.0
		self.distance = 25.0

		self.timer = wx.Timer( self )
		self.timer.Start( 30, False )
		
		self.size = None
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
		self.Bind(wx.EVT_TIMER, self.AutoRefresh, self.timer )
		
		self.groovikRenderer = GroovikGLRenderer()
		self.SetFocus()
		
		moveLogger = GLog("moves.log");
		moveLogger.logLine("[ \"reset\" ]");
		
		self.grooviksCube = groovik.GrooviksCube( moveLogger )
		curTime = time.clock()
		self.grooviksCube.SetStartTime( curTime )
		
		# simulate one frame so we have a valid state to render on first frame
		self.Simulate( None ) 
		
		self.__keysDown = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
		self.simTimer = wx.Timer( self )
		self.simTimer.Start( 100, False )
		self.Bind(wx.EVT_TIMER, self.Simulate, self.simTimer )
		self.Refresh(False)		

	def AutoRefresh( self, event ):
		self.Refresh(False)

	def OnEraseBackground(self, event):
		pass # Do nothing, to avoid flashing on MSW.

	def OnSize(self, event):
		self.size = self.GetClientSize()
		event.Skip()

	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		self.SetCurrent()
		self.groovikRenderer.Draw( self.size.width, self.size.height, self.altitude, self.azimuth, self.distance, self.grooviksCube.GetFaceColors() )
		self.SwapBuffers()

	def OnMouseDown(self, evt):
		self.CaptureMouse()
		self.lastx, self.lasty = evt.GetPosition()

	def OnMouseUp(self, evt):
		self.ReleaseMouse()

	def OnMouseMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			self.azimuth += 0.006 * ( self.lastx - evt.GetPosition().x )
			self.altitude += 0.008 * ( self.lasty - evt.GetPosition().y )
			self.altitude = max( 0.01, min( 3.14, self.altitude ) )
			self.lastx, self.lasty = evt.GetPosition()
			self.Refresh(False)
		if evt.Dragging() and evt.RightIsDown():
			self.distance *= pow( 1.01, 0.4 * ( evt.GetPosition().y - self.lasty ) )
			self.lastx, self.lasty = evt.GetPosition()
			self.Refresh(False)
		
	def Simulate( self, event ):
		simTime = time.clock()
		keyframes, resync = self.grooviksCube.Update( simTime )
		self.groovikRenderer.QueueKeyframes( keyframes )
	
	def ResetColors(self):
		# reset colors
		self.grooviksCube.ResetColors()
		self.Refresh(False)

	def OnKeyDown(self, event):
		key = event.GetKeyCode()
		if ( key == ord('Z') ):
			self.ResetColors()
		elif ( key == ord('A') ):
			self.groovikRenderer.ToggleDrawAxes()
		elif ( key == ord('C') ):
			self.groovikRenderer.ToggleDrawColorTransitions()
		elif ( key == ord('W') ):
			groovikConfig.SaveConfig()
		elif ( key == ord('L') ):
			groovikConfig.LoadConfig()
		elif ( key == ord('M') ):
			currentMode = self.grooviksCube.GetCurrentMode() + 1
			currentMode = currentMode % CubeMode.CUBE_MODE_COUNT
			self.grooviksCube.HandleInput( CubeInput.SWITCH_MODE, currentMode )
		elif ( key == ord('S') ):
			if ( event.ShiftDown() ):
				self.grooviksCube.rotationTime += 0.1
			else:
				self.grooviksCube.rotationTime -= 0.1
				if ( self.grooviksCube.rotationTime < 0.1 ):
					self.grooviksCube.rotationTime = 0.1
			print "new rotation time : "
			print self.grooviksCube.rotationTime
		elif ( key >= ord('1') and key <= ord('9') ):
			rot = key - ord('1')
			self.__keysDown[ rot ] = 1
		
	def OnKeyUp(self, event):
		key = event.GetKeyCode()
		if ( key >= ord('1') and key <= ord('9') ): # Checks for between '1' and '9'
			rot = key - ord('1')
			if ( not self.__keysDown[ rot ] ):
				return
			params = []
			base = int( rot / 3 ) * 3
			for i in range( base, base + 3 ):
				if ( self.__keysDown[ i ] ):
					params.append( [ i, event.ShiftDown() ] )
					self.__keysDown[ i ] = 0
			self.grooviksCube.HandleInput( CubeInput.ROTATION, params )		

class MainWindow(wx.Frame):
	def __init__(self, parent = None, id = -1, title = "PyOpenGL Example 1"):
		# Init
		wx.Frame.__init__(
			self, parent, id, title, size = (600,600),
			style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
		)

		# TextCtrl
		# self.control = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE)

		self.Show( True )

		self.control = GroovikCanvas(self)
		self.Layout()

		# StatusBar
		self.CreateStatusBar()

		# Filemenu
		filemenu = wx.Menu()

		# Filemenu - About
		menuitem = filemenu.Append(-1, "&About", "Information about this program")
		self.Bind(wx.EVT_MENU, self.OnAbout, menuitem) # here comes the event-handler
		# Filemenu - Separator
		filemenu.AppendSeparator()

		# Filemenu - Exit
		menuitem = filemenu.Append(-1, "E&xit", "Terminate the program")
		self.Bind(wx.EVT_MENU, self.OnExit, menuitem) # here comes the event-handler

		# Menubar
		menubar = wx.MenuBar()
		menubar.Append(filemenu,"&File")
		self.SetMenuBar(menubar)

		# Show
		self.Show(True)

	def OnAbout(self,event):
		message = "Using PyOpenGL in wxPython"
		caption = "About PyOpenGL Example"
		wx.MessageBox(message, caption, wx.OK)

	def OnExit(self,event):
		self.Close(True)  # Close the frame.

groovikConfig.SetConfigFileName( 'config_pc.txt' )
groovikConfig.LoadConfig()
app = wx.PySimpleApp()
frame = MainWindow()
app.MainLoop()

# destroying the objects, so that this script works more than once in IDLEdieses Beispiel
del frame
del app
