
from groovikutils import *

class GrooviksClient:

    def __init__( self, cube, id, logger ):
        self.__cube = cube
        self.__id = id
        self.__state = ClientState.IDLE
        self.__logger = logger
    
    def LogEvent( self, str ):
        if ( self.__logger != None ):
            self.__logger.logLine( str )

    def GetCube(self):
        return self.__cube
    
    def GetID(self):
        return self.__id

    def GetState(self):
        return self.__state
    
    def GetPosition(self):
        return self.__id
    
    def SetState(self, newState):
        self.__state = newState
        # TODO: something cause the new state to be published?
    
    def HandleCommand(self, command, parameters):
        '''
        Choose the appropriate action for the command, based on the current
        client state.  If there is no mapping for the current state, the 
        command is treated as invalid and ignored.
        '''
        actionMap = GrooviksClient.COMMAND_MAP[command]
        try:
            actionMap[self.GetState()](self, parameters)
        except KeyError:
            self.LogEvent("Cannot execute command <TODO> in state %s" % (self.GetState()))

    #--------------------------------------------------------------
    # Actions
    #--------------------------------------------------------------
    def WakeFromIdle( self, parameters ):
        newState = {
                    GameState.UNBOUND :             ClientState.HOME,
                    GameState.SINGLE :              ClientState.HOME,
                    GameState.SINGLE_INVITE :       ClientState.MULT,
                    GameState.MULTIPLE :            ClientState.MULT,
                    GameState.VICTORY :             ClientState.VICT,
                    }[self.GetCube().GetGameState()]
        self.SetState(newState)

    def QuitFromHome(self, parameters):
        self.SetState(ClientState.IDLE)

    def QuitFromSingle(self, parameters):
        self.SetState(ClientState.IDLE)
        self.GetCube().SinglePlayerExits()
        
    def QuitFromMultiple(self, parameters):
        self.SetState(ClientState.IDLE)
        self.GetCube().MutiplePlayerExits(self)
        
    def RestartFromSingle(self, parameters):
        raise "Not implemented"
        
    def RestartFromMultiple(self, parameters):
        # SINGLE_INVITE:
        #   If the third player is idle:
        #     clientState <= HOME
        # MULTIPLE:
        #   If other two are idle:
        #     clientState <= HOME_RESTART
        #     cubeState <= UNBOUND
        #   Else:
        #     clientState <= MULTIPLE_DIFFICULTY
        #     cubeState <= MULTIPLE_RESTART
        # MULTIPLE_RESTART:
        #   clientState <= MULTIPLE_DIFFICULTY
        #   If all non-IDLE players are also MULTIPLE_DIFFICULTY:
        #     cubeState <= MULTIPLE
        #
        raise "Not implemented"     
        
    # TODO: it looks like Start1P and Start3P should probably be factored
    def Start1P(self, parameters):
        gameState = self.GetCube().GetGameState()
        if gameState == GameState.UNBOUND:
            newState = {
                        ClientState.HOME :          ClientState.SING,
                        }[self.GetState()]
            self.LogEvent("Starting single player mode")
            self.SetState(newState)
            self.GetCube().SinglePlayerStarts(self)
        elif gameState == GameState.SINGLE:
            # TODO: start local play
            self.LogEvent("Request to begin single player mode in game state SINGLE")
        else:
            self.LogEvent("Request to begin single player mode in game state %s" % (gameState))

    def Start3P(self, parameters):
        gameState = self.GetCube().GetGameState()
        if gameState == GameState.UNBOUND:
            newState = {
                        ClientState.HOME :          ClientState.MULT,
                        }[self.GetState()]
            self.SetState(newState)
            self.GetCube().SinglePlayerStarts(self)
        elif gameState == GameState.SINGLE:
            # TODO: start local play
            pass  
        
    def Scramble(self, parameters):
        difficulty = parameters['difficulty']
        self.GetCube().Randomize(difficulty)

    COMMAND_MAP = {
        ClientCommand.WAKE : {
            ClientState.IDLE :              WakeFromIdle,
        },
        ClientCommand.QUIT : {
            ClientState.HOME :              QuitFromHome,
            ClientState.SING :            QuitFromSingle,
            ClientState.MULT :          QuitFromMultiple,
        },
        ClientCommand.START_1P : {
            ClientState.HOME :              Start1P,
        },
        ClientCommand.START_3P : {
            ClientState.HOME :              Start3P,
        },
        ClientCommand.SELECT_DIFFICULTY : {
            ClientState.SING :        Scramble,
            ClientState.MULT :                 Scramble,
        },
    }

