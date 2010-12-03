#imports 

#import standard libraries
import fileinput
import time
import socket

#import uistation;
from uistation import UiStation
from UIManager import UIManager;

#import extensions
import serial

#import our own binaries
import groovik
import lightboard
import display

from uistation import UiStation

import sys;

ui = UIManager();

lasttime = time.time();

while(True):      
   #sample the input
   result = ui.update();
   if result:
      command = result[0];
      # if this is a rotation...
      if (command < 18):
         rot = command / 2;
         reverse = command % 2;
         print "control pushed";
         print command;
      
