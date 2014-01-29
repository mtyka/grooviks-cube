#!/usr/bin/env python
""" producer.py
Produces random data samples for the EQ sliders.
Uses the Hookbox REST api for publishing the data
on channel "iframe".

--- License: MIT ---

 Copyright (c) 2010 Hookbox

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.

"""

import copy
import fileinput
import json
import math
import random
import sys
import threading
import time
import datetime
import urllib, urllib2
import display
import serial
import lightboard
import json

import groovik
from hbclient import *
from glog import GLog
from groovikutils import *
from groovikconfig import *
from GScript import GScript

TARGET_FRAMERATE = 3
TARGET_FRAMETIME = 1.0 / TARGET_FRAMERATE
INACTIVITY_TIMEOUT = 125

# 30 looks good on real PCs.  iphones and ipads max out at about 5-10.
# TODO: publish multiple channels at different framerates

# Ensure the cube is only accessed form one thread at a time
cube_lock = threading.Lock()

def compress_datagram(datagram):
	"""Returns a JSON object to be sent through hookbox.
	"""

	hex_datagram = ''

	for facet in datagram:
		for rgb in facet:
			hexval = "%02x" % (rgb * 255)
			hex_datagram += hexval

	output = '"%s"' % hex_datagram
	#print "sending %s" % output
	return output

last_datagram_sent = None
last_datagram_sent_timestamp = datetime.datetime.now()

class IntervalGenerator():
  """Creates and manages an interval which has a mean and a flat random distribution
	 around that mean with a width of width."""

  def __init__( self, mean, width ):
	self.interval_mean = mean
	self.interval_width = width
	self.current_interval = self.generate_interval()

  def generate_interval( self ):
	## intervals can't be < 0 obviously
	return max( self.interval_mean + (random.random()-0.5) * self.interval_width, 0 )

  def new_interval( self ):
	self.current_interval = self.generate_interval()

  def get_interval( self ):
	return self.current_interval


def compress_rgbfloat(rgb):
	"""Returns a JSON object to be sent through hookbox.
	"""

	datagram = ''

	for color in rgb:
		val = "%f " % color
		datagram += val

	output = '"%s"' % datagram
	#print "sending %s" % output
	return output

def too_long_since_last_datagram():
	"""Check if it's been more than a couple of seconds since we sent the last
	datagram.  If not, so, return True.
	This keeps a minimum framerate, which effectively acts as iframes for new clients
	"""
	how_long_ago = datetime.datetime.now() - last_datagram_sent_timestamp
	threshhold = datetime.timedelta(0,3) # seconds
	return how_long_ago > threshhold


def push_datagram(datagram):
	global last_datagram_sent
	global last_datagram_sent_timestamp
	if datagram == last_datagram_sent:
		# In general we don't want to send repeated frames.
		if not too_long_since_last_datagram():
			return
	else:
		last_datagram_sent = datagram

	last_datagram_sent_timestamp = datetime.datetime.now()
	push_message( compress_datagram(datagram), "iframe")

def push_game_client_state( cube ):
	active_position = cube.GetActivePosition()
	if active_position == None:
		active_position = 0

	game_state = cube.GetGameState()
	clients = cube.GetAllClients()
	client_state = []
	for client in clients:
		client_state.append( client.GetState() )

	gs_dict = { 'gamestate':game_state, 'clientstate':client_state, 'active_position':active_position.__str__()  }
	push_message( json.dumps(gs_dict), 'gameState' )

class Cube():
	def __init__(self):

		self.lastRotationStep = 0

		count = 257;
		self.displayc = display.Display(count, "input_playa.py" )

		# connect to the hookbox client and receive commands
		groovikConfig.SetConfigFileName( 'config_pc.txt' )
		groovikConfig.LoadConfig()

		self.logger = GLog("moves.log");
		self.logger.logLine("[ \"reset\" ]");

		self.grooviksCube = groovik.GrooviksCube( self.logger, self.displayc )
		curTime = time.time()
		self.simTime = curTime;
		self.grooviksCube.SetStartTime( curTime )

		# used for initiating server-side timeouts
		self.positionForUser = {}
		self.clientLastActivity = {}

		#used for idling cube moves
		self.lastIdleMove = 0.0
		self.interval = IntervalGenerator(  8.0,  6.0 )

		# simulate one frame so we have a valid state to render on first frame
		# self.simulate()

		client = HookClient(self.process_commands)
		client_thread = threading.Thread(target = client.run)
		client_thread.setDaemon(True)
		client_thread.start()

	def process_commands(self, rtjp_frame):

		action, params = rtjp_frame[1:3]

		if action == "PUBLISH":
			channel, payload, user = params['channel_name'], params['payload'], params['user']
			print "Recv stuff: ", channel, payload, user
			try:
				if channel == 'faceclick':
					face, rot_command = payload[0], payload[1:]
					#print rot_command
					with cube_lock:
						# callbacks for both rotation and pixel click
						# better way of doing this?
						self.grooviksCube.HandleInput( CubeInput.ROTATION, [rot_command])
						self.grooviksCube.HandleInput( CubeInput.FACE_CLICK, face)
						#self.grooviksCube.QueueEffect( "victory0" )
					self.resetClientTimeout(user)
				elif channel == 'clientcommand':
					'''This channel is used for sending commands to change the game state'''
					position = int(payload.pop('position'))
					command = payload.pop('command')
					self.logger.logLine( "Received command '%s' from client at position %d with arguments %s" % (command, position, payload) )
					self.grooviksCube.HandleClientCommand(position, command, payload)
					push_game_client_state(self.grooviksCube)
					if command != ClientCommand.QUIT:
						self.resetClientTimeout(user, position)

				elif channel == 'gamemode':
					self.logger.logLine( "Received commmand for defunct channel 'gamemode' %s " % (payload) )

				elif channel == 'cubemode':
					mode = payload['mode']
					self.logger.logLine( "CubeMode: %s " % (payload) )
					if( self.grooviksCube.GetCurrentMode() != mode):
						self.grooviksCube.QueueModeChange(mode)
				elif channel == 'colorcalib':
					command = rtjp_frame[2]['payload']
					print command
					if ( len(command) == 1 ):
						push_message( compress_rgbfloat(self.displayc.lm.getPixelOffset(command[0])), "colorcalibrx")
						return
					with cube_lock:
						self.logger.logLine( "Color calibration: Pixel, (R G B) = %s " % (command) )
						self.grooviksCube.HandleInput( CubeInput.COLOR_CAL,command)

				elif channel == 'settings':
					if str(payload['command']) == 'get':
						groovikConfig.getSettings()
					elif str(payload['command']) == 'set':
						groovikConfig.setSettings(payload['vals'])

				elif channel == 'vote':
					if 'vote' in payload and self.grooviksCube.isVoteOpen():
						self.grooviksCube.submitVote(int(payload['position']), int(payload['vote']))
					elif 'vote-initiate' in payload:
						self.grooviksCube.startVote(int(payload['vote-initiate']))

			except KeyError:
				#TODO: actually parse the error and log it
				pass
			except Exception, msg:
				self.logger.logLine("Swallowed exception '%s' raised during command handling in hookbox while handling command on %s " % (msg, channel))

	def resetClientTimeout( self, user, position = None ):
		if position is None:
			try:
				position = self.positionForUser[user]
			except KeyError:
				self.logger.logLine("Failure to reset timeout for unknown user %s" % (user))
		else:
			self.positionForUser[user] = position
		self.clientLastActivity[position] = time.time()

	def checkTimeouts( self ):
		'''
		Check if any clients have been inactive for too long, and send a 'QUIT'
		client command for each of those clients.
		'''
		now = time.time()
		for position, last_activity in self.clientLastActivity.items():
			if now - last_activity > INACTIVITY_TIMEOUT:
				self.logger.logLine("Client at position %s inactive for %d seconds; timing out" % (position, now - last_activity))
				push_message( json.dumps({ 'position':position, 'command':ClientCommand.QUIT, }), 'clientcommand' )
				del self.clientLastActivity[position]
				for user, position_ignored in self.positionForUser.items():
					del self.positionForUser[user]

	def executeIdlingMoves( self ):
		'''
		Check if there's been no activity for longer than a certain period. If so
		execute random cube moves every so often such that the cube is animated while noone is playing
		'''
		now = time.time()
		most_recent_activity = max(self.clientLastActivity.values() + [0.0])
		#print self.clientLastActivity.values(), most_recent_activity, self.lastIdleMove
		## should we be doing random idling moves ?
		idlemoves_delay = 25.0 #seconds

		if (self.grooviksCube.GetGameState() == "UNBOUND" and
			(now - most_recent_activity) > idlemoves_delay and
			(now - self.lastIdleMove) > self.interval.get_interval() ):
		  self.grooviksCube.RandomUnboundIdleMove()
		  self.lastIdleMove = now
		  self.interval.new_interval()

	def interpolateFrames( this, data, passedTime, dataLast ):
		if not data:
			return dataLast;
		beforeTime = 0.0
		afterTime = 0.0
		passedTick = passedTime / 0.004
		for i in range( len( data ) ):
			beforeTime = afterTime
			afterTime += data[i][0]
			if ( passedTick >= beforeTime and passedTick <= afterTime ):
				if ( i == 0 ):
					before = dataLast
				else:
					before = data[i-1][1]
				after = data[i][1]
				if ( len(before) == 0 ):
					before = after
				lerpedColors = []
				c = []
				if ( afterTime != beforeTime ):
					t = ( passedTick - beforeTime ) / ( afterTime - beforeTime )
				else:
					t = 1.0
			   # print str( passedTime ) + " b " + str( beforeTime ) + " a " + str( afterTime ) + " t " + str(t) + " bc " + str( before[0] ) + " ac " + str( after[0] )
				for j in range( 54 ) :
					c = BlendColorsRGB( before[j], after[j], t )
					lerpedColors.append( c[:] )
				return lerpedColors
		if (len(data) == 0):
			return dataLast
		else:
			return data[-1][1];

	def run(self):
		lastFrameLerpedColors = []
		while True:
			self.displayc.loop()

			frameStartTime = time.time()

			data, rotationStep = self.simulate()
			# generate random colors for every cube face every 1.5 seconds
			# and publish them via the HTTP/REST api.

			frameLerpedColors = []
			self.simTime = self.simTime + TARGET_FRAMETIME;

			# This instructs the clients to play rotation sounds
			# Dont do this in UNBOUND (idle) mode, because it gets annoying.
			if rotationStep != self.lastRotationStep :
				self.lastRotationStep = rotationStep
				if self.grooviksCube.GetGameState() != "UNBOUND":
				  push_message(rotationStep, "rotationStep")

			while ((self.simTime - time.time()) > (TARGET_FRAMETIME/3)):
				# Here we will want to interpolate across the frames, or if there are none use current state.
				frameLerpedColors = self.interpolateFrames( data, time.time()- frameStartTime, lastFrameLerpedColors );
				time.sleep(0.02)
				if ( len(frameLerpedColors) > 0 ):
					push_datagram( frameLerpedColors );


			lastFrameLerpedColors = data[-1][1];

			self.checkTimeouts()
			self.executeIdlingMoves()

	def simulate(self):
		with cube_lock:
		  keyframes, resync, rotationStep = self.grooviksCube.Update( self.simTime );
		  self.displayc.renderFrames( keyframes, resync )
		if keyframes:
			return keyframes, rotationStep

if __name__ == "__main__":
	cube = Cube()
	cube.run()
