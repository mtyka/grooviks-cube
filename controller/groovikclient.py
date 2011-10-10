
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

    def WakeFromIdle( self ):
        newState = {
                    GameState.UNBOUND :             ClientState.HOME,
                    GameState.SINGLE :              ClientState.HOME,
                    GameState.SINGLE_INVITE :       ClientState.MULT,
                    GameState.MULTIPLE :            ClientState.MULT,
                    GameState.VICTORY :             ClientState.VICT,
                    }[self.GetCube().GetState()]
        self.SetState(newState)

    def QuitFromHome(self):
        self.SetState(ClientState.IDLE)

    def QuitFromSingle(self):
        self.SetState(ClientState.IDLE)
        self.GetCube().SinglePlayerExits()
        
    def QuitFromMultiple(self):
        self.SetState(ClientState.IDLE)
        self.GetCube().MutiplePlayerExits(self)
        
    def RestartFromSingle(self):
        raise "Not implemented"
        
    def RestartFromMultiple(self):
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
    def Start1P(self):
        gameState = self.GetCube().GetGameState()
        if gameState == GameState.UNBOUND:
            newState = {
                        ClientState.HOME :          ClientState.SING,
                        }[self.GetState()]
            self.SetState(newState)
            self.GetCube().SinglePlayerStarts(self)
        elif gameState == GameState.SING:
            # TODO: start local play
            pass  

    def Start3P(self):
        gameState = self.GetCube().GetGameState()
        if gameState == GameState.UNBOUND:
            newState = {
                        ClientState.HOME :          ClientState.MULT,
                        }[self.GetState()]
            self.SetState(newState)
            self.GetCube().SinglePlayerStarts(self)
        elif gameState == GameState.SING:
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
            ClientState.SING_RESTRICTED :        Scramble,
            ClientState.MULT :                 Scramble,
        },
    }

