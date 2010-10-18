#/usr/bin/python
import time
from ctypes import *

gaudio = CDLL("grooviksaudio.so")

gaudio.Init()
gaudio.PlayStoneSound()
time.sleep(3)
gaudio.Close()
