#!/usr/bin/env python
import sys, os, asyncore, websocket
import random
import rtjp_eventlet.core as core
import threading

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

  def on_message(self, m):
    self.callback(core.deserialize_frame(m))
    
  def run(self):
    asyncore.loop()
