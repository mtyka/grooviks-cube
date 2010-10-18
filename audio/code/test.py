from ctypes import *

gaudio = CDLL("./grooviksaudio.so")

gaudio.test()
