# Introduction #
The server architecture consists of a few major elements:
  1. The main simulation object. This keeps track of, and is in control of updating, the color of the 54 cube "pixels".
  1. Simulation "state" objects. These are tasks that operate on the main simulation object. Only one "state" object can operate on the cube at a time.
  1. Cube "modes". These represent the type of game being played on the cube. One one game mode can be active at any time.
  1. Input messages. These represent control messages sent to the simulation by a remote client.
# Details #
## Files of Interest ##
  1. Groovikwx.py: Run this to run the project. It contains the WX-widgets specific stuff to create the window + handle keypresses. It also creates the simulation object + renderer object.
  1. Groovikgl.py: This contains the GL-based renderer to render the cube state, split out to hopefully make for easier integration into the new client.
  1. Groovik.py: This contains the cube simulation object
  1. Mode`*`.py: These contain the game modes. See modebase.py for the mode interface.
  1. State`*`.py: These contain the cube simulation states. See statebase.py for the state interface.
## Game Modes ##
Game modes (found in files named mode`*`.py) are hooked into the main simulation object, and it calls the mode in the following circumstances:
  * Whenever the mode starts. Here, the mode must define a list of unique colors that will be visible on the cube and return an array of 54 indices into that list of unique colors to use as an initial condition
  * Whenever an “input event” occurs. Here, the game mode can respond to the input event by queueing a state change onto the simulation object.
  * Every simulation step the game mode is called to check if it wants to queue a new state change on the simulation object. For example, the game mode can detect here if the cube is solved and switch to a victory condition.
  * Every time a state change is about to be queued on the simulation object, the game mode is called to see if it will allow the state change to be queued. This is used to allow the game mode to suppress state changes while in its victory mode, for example.
## Cube States ##
Cube states (found in files named state`*`.py) are used by the main simulation object to modify the state of the cube pixel colors(i.e. a rotation or a victory effect, like a fade). Only one cube state can be active at a time. Cube states are available for use by any game mode, but game modes need not use all the states. I’ve created an interface documenting how to implement more cube states in statebase.py.
## Main Simulation Object ##
The responsibility of the main simulation object has been reduced from the playa version. Now, it just has a current state which is modifying the cube face colors, and a queue of requested state changes.
## Input Messages ##
We had some conversations about how generic the input state should be, and the current decision was to make them higher-level. So, my code currently assumes there is only two types of inputs being sent by the controls panels: a rotation request, and a mode switch request. These inputs have a parameter list sent along with them; in the case of the rotation request, it sends an integer indicating the rotation type, and a bool indicating whether it’s clockwise. For the mode switch request, it sends an enum indicating the mode to switch to. The game modes can interpret these requests however they want, generating queued cube states for the simulation object. For example, the color correction configuration mode uses the “rotation” request to switch to the next color to switch the cube to; it doesn’t perform a rotation at all, and it also ignores the input parameters.