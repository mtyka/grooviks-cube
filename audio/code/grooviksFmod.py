#/usr/bin/python
import os
import sys
import time
import ctypes

class GrooviksFmod:
    def __init__(self):
        scriptPath =  os.path.abspath(os.path.dirname(__file__))
        ctypes.cdll.LoadLibrary(os.path.join(scriptPath, "fmodapi/lib/libfmodex64.so"))
        ctypes.cdll.LoadLibrary(os.path.join(scriptPath, "fmodapi/lib/libfmodevent64.so"))
        self.grooviksAudio = ctypes.CDLL(os.path.join(scriptPath,"grooviksaudio.so"))
        self.grooviksAudio.Init.restype = ctypes.c_void_p
	self.eventSystem = self.grooviksAudio.Init(os.path.join(scriptPath,"../build/"))

    def PlayStoneSound(self):
	self.grooviksAudio.PlayStoneSound(self.eventSystem)
    
    def __del(self):
        self.grooviksAudio.Close(self.eventSystem)
        
