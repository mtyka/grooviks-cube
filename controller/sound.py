import pygame
import time
import random
import threading 

audio_lock = threading.RLock()

def init_sound():
   pygame.mixer.init(44100, -16, 1)

"""
SoundSets can be made up of different (sound files, vol) tuples and other SoundSets
A SoundsSet has a 'play' mode, defaults to random, changed by playfunc, arguments are determined by pfkwargs

s = sound.SoundSet(["audio_samples/1.wav","audio_samples/2.wav", "audio_samples/3.wav"])
s2 = sound.SoundSet(["audio_samples/1.wav","audio_samples/2.wav", "audio_samples/3.wav"], {"simult":[2]})
ss = sound.SoundSet([s,s2])
ss.play_seq(), etc, etc
"""
class SoundSet(object):
   def __init__(self, sounds, pfkwargs = {}):
      self.__sounds = []
      self.__run = False
      self.__pfkwargs = pfkwargs
      for f in sounds:
         if type(f) == type(tuple()):
            with audio_lock:
               self.__sounds.append(pygame.mixer.Sound(f[0]))
               self.__sounds[-1].set_volume(f[1])
         else:
            self.__sounds.append(f)

   def play(self, loop = 0):
      return self.play_random(loop, **self.__pfkwargs)

   # returns length
   def play_index(self, index, loop = 0):
      s = self.__sounds[index]
      with audio_lock:
         s.play(loop)
         return s.get_length()*(1+loop)

   # returns length
   # simult is a set of simultaneous random samples to play
   # which itself is picked from randomly
   def play_random(self, loop = 0, simult=[1]):
      snds = set()
      simult = min(len(self.__sounds), random.choice(simult))
      while (len(snds) != simult):
         snds.add(random.choice(self.__sounds))
      max_len = 0
      for s in snds:
         dur = 0
         with audio_lock:
            if type(s) == type(self):
               dur = s.play()
            else:
               dur = s.get_length()
               s.play()
         max_len = max(max_len, dur)
      return max_len*(1+loop)

   def play_seq(self, loop = 0):
      def seq_func(self):
         for x in range(0, loop+1):
            for s in self.__sounds:
               if not self.__run:
                  return
               dur = 0
               with audio_lock:
                  if type(s) == type(self):
                     dur = s.play()
                  else:
                     dur = s.get_length()
                     s.play()
               time.sleep(dur)

      t = threading.Thread(target = seq_func, args = [self])
      t.daemon = True
      self.__run = True
      t.start()

   def stop(self):
      self.__run = False
      for s in self.__sounds:
         s.stop()


class MusicManager(object):
  """
  music_sets - list of files
  sounds sets - list of (prob, sound_set) tuples
  """ 
  def __init__(self, music_sets, sound_sets):
    self.__fade_time = 2000
    self.__ms = music_sets
    self.__as = sound_sets
    self.__play_sounds = False
    self.__play_music = False
    self.__ind = 0
    self.__mt = threading.Thread(target = self.__music_loop)
    self.__mt.deamon = True
    self.__mt.start()

  def set_music_index(self, index):
    self.__ind = index

  """
  should ambient sounds be played?
  """
  def set_sound_on(self, sound_on):
    with audio_lock:
      self.__play_sounds = sound_on

  def set_music_on(self, music_on):
    with audio_lock:
      self.__play_music = music_on

  def __music_loop(self):
    current = self.__ind
    playing = self.__play_music

    while True:
      with audio_lock:
        if playing != self.__play_music or current != self.__ind:
          if playing:
            pygame.mixer.music.fadeout(self.__fade_time)
          playing = self.__play_music
          current = self.__ind
      if playing:
        if not pygame.mixer.music.get_busy():
          m = random.choice(self.__ms[current])
          with audio_lock:
            pygame.mixer.music.load(m[0])
            pygame.mixer.music.set_volume(m[1])
            pygame.mixer.music.play() # repeat forever!
      
      if self.__play_sounds:
        for s in self.__as:
          num = random.randrange(0,10000)
          if num < s[0]*10000:
            with audio_lock:
              s[1].play()
      time.sleep(1)
    
"""
tests
"""
if __name__ == "__main__":
  init_sound()  
  s1 = SoundSet([("as/1.wav",1.0)])
  s2 = SoundSet([("as/2.wav",1.0)])
  sc = SoundSet([s1, s2])
  
  s1.play()
  s2.play()
  sc.play()
  sc.play_seq()

  m = MusicManager([[("as/1.ogg",1.0), ("as/2.ogg",1.0), ("as/3.ogg",1.0)], 
                    [("as/4.ogg",1.0)]], 
                    [(.5, s1), (.1, s2)])
  try:
    print "music start..."
    m.set_music_on(True)
    time.sleep(5.0)
    print "sounds off"
    m.set_sound_on(False)
    time.sleep(10.0)
    print "change index"
    m.set_music_index(1)
    time.sleep(10.0)
    print "stop music"
    m.set_music_on(False)
    time.sleep(10.0)
    print "sounds on/music on/first set"
    m.set_music_index(0)
    m.set_music_on(True)
    m.set_sound_on(True)
    inp = raw_input("press enter to stop")
  except KeyboardInterrupt:
    m.set_music_on(False)
    print "\nstopping music..."
    time.sleep(2.0)
  import sys
  sys.exit(0)

    




