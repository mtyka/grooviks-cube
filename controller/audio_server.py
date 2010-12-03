#!/usr/bin/env python

from event_manager import *
from sound import *
import pygame
import threading

audio_client_addr = "10.0.0.2"
cube_event_server_addr = "10.0.0.1"
audio_client_port =  65006
cube_event_server_port = 64005
cube_delay_hack = 0.0

debug = True


class FutureTheme(object):
   def __init__(self):
      
      t1 = SoundSet([("as/stone_gears_002.wav", 1.0)])
      a11 = SoundSet([("as/1-1.wav", 0.7)])
      a12 = SoundSet([("as/1-2.wav", 0.7)])
      a13 = SoundSet([("as/1-3.wav", 0.7)])
      a21 = SoundSet([("as/2-1.wav", .9)])
      a22 = SoundSet([("as/2-2.wav", .9)])
      a23 = SoundSet([("as/2-3.wav", .9)])
      a31 = SoundSet([("as/3-1.wav", 1.0)])
      a32 = SoundSet([("as/3-2.wav", 1.0)])
      a33 = SoundSet([("as/3-3.wav", 1.0)])

      self.rotate = [
         [ SoundSet([a11,t1]), SoundSet([a12,t1]), SoundSet([a13,t1]) ],
         [ SoundSet([a21,t1]), SoundSet([a22,t1]), SoundSet([a23,t1]) ],
         [ SoundSet([a31,t1]), SoundSet([a32,t1]), SoundSet([a33,t1]) ],
      ]

      amb1 = SoundSet([("as/amb_oneshot_trippy_echo_001.wav", .5),
                       ("as/amb_oneshot_spooky_sizzle_001.wav", .5),
                       ("as/amb_oneshot_machine_rattle_003.wav", .5),
                       ("as/amb_oneshot_monorail_001.wav", .5),
                       ("as/amb_oneshot_nascar_001.wav", .5),
                       ("as/amb_oneshot_timestretch_001.wav", .5),
                     ])
      amb2 = SoundSet([
                       ("as/amb_oneshot_vox_drugme_001.wav", .05),
                       ("as/amb_oneshot_vox_hawking_003.wav", .4),
                     ])
      self.music = MusicManager([[("as/ambient.ogg", .4)]], [(.07, amb1), (.002, amb2)])

"""
Audio event listener
"""
class AudioCube(CubeEventListener):      
   def __init__(self):
      pass

   def connect(self):
      print "connect"
      theme.music.set_sound_on(True)
      theme.music.set_music_on(True)

   def disconnect(self):
      print "disconnect"
      theme.music.set_sound_on(False)
      theme.music.set_music_on(False)

   def rotate(self, axis, rows, direction, length):
      time.sleep(cube_delay_hack)
      for r in rows:
         theme.rotate[axis][r].play_seq()
   def reward(self, level):
      pass
   def punish(self, level):
      pass
   def set_solve_level(self, level):
      pass
   def invalid_move(self, axis):
      pass
   def idle(self, type):
      pass


theme = None
if __name__ == "__main__":
   init_sound()
   theme = FutureTheme()
   connect_cube_event_listener(AudioCube(), audio_client_addr, audio_client_port, cube_event_server_addr, cube_event_server_port)
   inp = raw_input("Hit return to stop listening.")

