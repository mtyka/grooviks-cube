# Introduction #

The client will hopefully be connected via http to a server that will control the game state.

Main use cases:
  * In Pacific Science center, up to 3 tablets control the real cube in an intuitive way. This may or may not involve some display of the actual cube on the tablet.
    * The current plan is to use a local webserver and have the tablet/touchscreens configured to talk to the local game server which will in turn control the real cube
  * On the web, up to N combinations of up to 3 players control a shared cube. This component's primary purpose is to test the cube UI. As such, the cube state might be on a separate page/iframe/etc from the actual control.
    * We would like the option of deploying this software to the world at large for them to prepare for a possible cubing competition at the pacsci center.


# Details #

## WebGL as a platform ##
WebGL seems technologically like an ideal solution to our desire to make a web controllable cube game, but it may be overkill. The number of computers deployed today with WebGL support is extremely tiny. You basically have to download a dev channel version of Chromium and run with a command line flag.

Because the Cube is such a simple object and we're not even sure if it makes sense to rotate in 3d, it probably makes more sense to think about using an HTML5 canvas instead, and simply faking 3d.