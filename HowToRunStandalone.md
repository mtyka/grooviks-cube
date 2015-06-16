# Introduction #

This page describes how to run the standalone GL and WX-based application to run the cube python code.

# Details #

## Installation ##
  * Install PyOpenGL http://pyopengl.sourceforge.net/
  * Install WxPython http://www.wxpython.org/. Note that I've only run this on the PC. Apparently, you need some special build of Python on the Mac called the Framework build to use wxPython on the Mac. I've split the wx-specific code out from the rest of this code; we could make a different Mac front end pretty easily if we wanted.

## Startup + Controls ##
Run **groovikwx.py** to start it up. Occasionally, it seems to lose key focus on startup. I find that minimizing + maximizing the window corrects it.

The following keys are currently supported:
  * '1' - '9': These perform the various rotations of the cube. Holding shift down while hitting these keys will perform the rotation in the opposite direction.
  * 'A' : Will toggle axis rendering
  * 'C' : Will toggle color swatch rendering (was used to help test color interpolation in various color spaces)
  * 'Z' : Resets the cube to its initial state
  * 'L' : Reloads the configuration files
  * 'W' : Writes the configuration files
  * 'M' : Toggles game mode
  * 'S' : Reduces cube rotation speed. Holding shift will hitting S increases rotation speed.