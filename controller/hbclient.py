#!/usr/bin/env python
import sys, os, asyncore, websocket
import random
import rtjp_eventlet.core as core
import threading
import urllib, urllib2

class HookClient:

	def __init__(self, callback):
		self.frame_id = 0
		self.cookie_id = str(random.randrange(0,200000000))
		self.callback = callback
		self.ws = websocket.WebSocket('http://127.0.0.1:2974/ws',
			onopen=self.on_open,
			onmessage=self.on_message,
			onclose=lambda: sys.stdout.write('Closed Socket\n'))

	def on_open(self):
		print('Socket Opened, Subscribing')
		self.ws.send(core.serialize_frame(self.frame_id, 'CONNECT', { 'cookie_string' : 'cookie_identifier='+self.cookie_id}))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'faceclick' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'movesfromsolved' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'gamemode' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'cubemode' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'colorcalib' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'colorcalibrx' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'clientcommand' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'turns' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'settings' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'vote' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'timeout' }))
		self.frame_id += 1
		self.ws.send(core.serialize_frame(self.frame_id, 'SUBSCRIBE', { 'channel_name' : 'difficulty' }))

	def on_message(self, m):
		self.callback(core.deserialize_frame(m))

	def run(self):
		asyncore.loop()

def push_message(message, channel):
	"""Pushes a message out onto a hookbox channel
	"""
	# assume the hookbox server is on localhost:2974
	url = "http://127.0.0.1:2974/rest/publish"

	values = { "secret" : "bakonv8",
			   "channel_name" : channel,
			   "payload" : message
			 }

	formdata = urllib.urlencode(values)
	req = urllib2.Request(url, formdata)
	resp = urllib2.urlopen(req)

	# the hookbox response can be useful for debugging,
	# but i'm commenting it out.
	#page = resp.read()
	#print page
