

# Screens #

There are ten distinct screens, each of which minimally presents some view of the cube and/or its controls, as well as menu options.  Each is briefly described below.  For more detailed descriptions and sample images, see the appendix, below.

| **Name** | **Description** |
|:---------|:----------------|
| Home     | Starting screen: presents option to start single- or multi-player session |
| Difficulty | Allows user to select difficulty of game |
| Single   | Single-player session, with control of main cube |
| Multiple-Invite | Informs user that the system is waiting for other player(s) to join multi-player session |
| Home-Invite | Like basic home screen, but only allows user to join the in-progress multi-player session |
| Multiple | Multi-player session with control of one axis of the main cube |
| Single-Invite | Single-player mode, with an option to promote session to a multi-player session |
| Local    | Single-player session, without control of the main cube (only displays on screen |
| Local-Invite | Local single-player session, with option to join multi-player session |
| Victory  | Displayed after the main cube has been solved |

# Global State #

## States ##

The main cube may be in one of six states:

| **State** | **Abbr** | **Description** |
|:----------|:---------|:----------------|
| Unbound   | U        | No session is in progress |
| Single    | S        | A single-player session is in progress |
| Single-Invite | I        | A single-player session is in progress, but another player has requested to switch to multi-player mode |
| Multiple  | M        | A multi-player session is in progress |
| Victory   | V        | The cube has been solved in multi-player mode |
| Admin     | A        | The cube is locked for administration tasks |

The _Single_ and _Single-Invite_ states represent cube sessions where the main cube is bound to (controlled by) a single user station.  The _Multiple_ state is used for cube sessions where the cube is locked in multi-player mode.  Note that this state (the cube state) is not sufficient to determine which appears on the client's screen; that is determined by a combination of the global cube state and the client state (see below).

## Transitions ##

Legal transitions are as follows:

| **Current State** | **New State** | **Description** |
|:------------------|:--------------|:----------------|
| Unbound           | Single        | Single player game requested |
| Unbound           | Multiple      | Multiple player game requested |
| Single            | Unbound       | The active player quits or times out |
| Single            | Single-Invite | Another station requests a multi-player game |
| Single-Invite     | Multiple      | The active player joins the multi-player session |
| Single-Invite     | Multiple      | The active player quits or times out |
| Single-Invite     | Single        | The player(s) requesting multi-player mode times out |
| Single-Invite     | Victory       | The cube is solved |
| Multiple          | Unbound       | All three players time out |
| Multiple          | Unbound       | One player requests a restart, and the other players are idle/local |
| Multiple          | Victory       | The cube is solved |
| Victory           | Multiple      | Automatic reset after victory sequence |
| (any state)       | Admin         | The administration interface is invoked |
| Admin             | (any state)   | Exit from administration interface |

| ![https://s3.amazonaws.com/grooviks-cube/global-state-3.jpg](https://s3.amazonaws.com/grooviks-cube/global-state-3.jpg) |
|:------------------------------------------------------------------------------------------------------------------------|
| **Figure 1: Global state machine**|

# Client State #

## States ##

| **State** | **Description** |
|:----------|:----------------|
| Idle      | The client is inactive, and the screen displays a screen saver |
| Home      | The client has a choice of starting a single- or multi-player session |
| Sing      | The client is in control of the main cube, and is presented with an option to restart |
| Mult      | The client is in control of one axis of the main cube, as part of a multi-player session |
| Vict      | The main cube has been solved, and the client must wait until the victory sequence is complete |
| Local     | The client is playing a single-player session, local to their station |
| Local-Difficulty | The client is playing a local single-player session, and is rescrambling the cube |
| Local-Victory | The client is playing a local single-player session, and has solved the cube |

## Transitions ##

| ![https://s3.amazonaws.com/grooviks-cube/client-state-2-sm.jpg](https://s3.amazonaws.com/grooviks-cube/client-state-2-sm.jpg) |
|:------------------------------------------------------------------------------------------------------------------------------|
| **Figure 2.  Client state machine.**  The names in the boxes correspond to client states; in some cases this has been annotated with a cube state (e.g. ":I") in order to demonstrate the the legal transitions from that client state depend on the global cube state.  Dotted lines indicate cube state transitions. |

# Appendix: Screen Details #

There are ten distinct screens, each of which minimally presents some view of the cube and/or its controls, as well as menu options.

| **Decription** | **Image** |
|:---------------|:----------|
| The home screen presents the user with two choices:  start a single player game, or start a multi-player game. | ![https://s3.amazonaws.com/grooviks-cube/Screen_Home.png](https://s3.amazonaws.com/grooviks-cube/Screen_Home.png) |
| The difficulty screen gives the user a choice of difficulty levels.  The options available might be restricted by recent history; for example, if the active station just solved the cube on "easy", then perhaps that difficulty level is unavailable.  As another example, the higher difficulty levels might be mad unavailable until the lower levels have been solved.<p>This screen also presents the option to go back to the home screen. <table><thead><th> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_Difficulty.png' /> </th></thead><tbody>
<tr><td> In single player mode, the active control station has sole and complete control over the cube, including rotation on any axis.  The screen does not display the colors on the main cube--only controls for manipulating it.<p>This screen also presents the option to go back to the home screen. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_Single.png' /> </td></tr>
<tr><td> When the user selects three player mode and chooses a difficulty level, they are taken to this screen to await other players joining.<p>This screen also presents the option to go back to the home screen. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_MultipleInvite.png' /> </td></tr>
<tr><td> When another user selects three player mode, the other two stations transition from the basic home screen to this screen.  This screen presents only the option to join the newly created three-player game. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_HomeInvite.png' /> </td></tr>
<tr><td> In multi-player mode, all active control stations show controls for a single axis of the cube.  As in single-player mode, the colors of the main cube are not visible on the screen.  Because the cube is only solvable in multi-player mode if two or more control stations are active, this screen is displayed only when two or more are active. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_Multiple.png' /> </td></tr>
<tr><td> While engaged in single-player mode, if another station requests a multi-player game, then the active single player is presented with a choice to join multi-player mode.  If they do this, then their session is promoted to a multi-player session without scrambling.<p>This screen also presents the option to go back to the home screen. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_SingleInvite.png' /> </td></tr>
<tr><td> If a user elects to enter single-player mode while another single-player session has control of the cube, that player will be presented with a local single-player session--that is, one which does not control the main cube, and is only present on their screen.  Unlike the main single-player mode, the colors of the cube do appear on the screen.  If the main single-player session ends, then this session may be promoted to the main cube.<p>This screen also presents the option to go back to the home screen. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_Local.png' /> </td></tr>
<tr><td> When the user is engaged in a local session, if another station requests multi-player mode, the local session is presented with an option to join the multi-player game, as with a single-player session on the main cube. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_LocalInvite.png' /> </td></tr>
<tr><td> When the main cube is solved, either in a single- or multi-player session, the screen displays victory sequence animations along with the main cube. </td><td> <img src='https://s3.amazonaws.com/grooviks-cube/Screen_Victory.png' /> </td></tr>