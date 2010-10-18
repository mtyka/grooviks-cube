#/usr/bin/python
import time
import ctypes

gaudio = ctypes.CDLL("grooviksaudio.so")
gaudio.Init.restype = ctypes.c_void_p
eventSystem = gaudio.Init()
gaudio.PlayStoneSound(eventSystem)
time.sleep(3)
gaudio.Close(eventSystem)
