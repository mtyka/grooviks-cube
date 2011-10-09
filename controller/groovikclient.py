
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
                    GameState.SINGLE_INVITE :       ClientState.MULTIPLE,
                    GameState.MULTIPLE :            ClientState.MULTIPLE,
                    GameState.MULTIPLE_RESTART :    ClientState.MULTIPLE,
                    GameState.VICTORY :             ClientState.VICTORY,
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
        self.SetState(ClientState.DIFFICULTY)
        
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
                        ClientState.HOME :          ClientState.SINGLE,
                        ClientState.HOME_RESTART :  ClientState.DIFFICULTY,
                        }[self.GetState()]
            self.SetState(newState)
            self.GetCube().SinglePlayerStarts(self)
        elif gameState == GameState.SINGLE:
            # TODO: start local play
            pass  

    def Start3P(self):
        gameState = self.GetCube().GetGameState()
        if gameState == GameState.UNBOUND:
            newState = {
                        ClientState.HOME :          ClientState.MULTIPLE,
                        ClientState.HOME_RESTART :  ClientState.MULTIPLE_DIFFICULTY,
                        }[self.GetState()]
            self.SetState(newState)
            self.GetCube().SinglePlayerStarts(self)
        elif gameState == GameState.SINGLE:
            # TODO: start local play
            pass  
        
    def Scramble(self, parameters):
        difficulty = parameters['difficulty']
        gameState = self.GetCube().GetGameState()
        newState = {
                    ClientState.DIFFICULTY :          ClientState.SINGLE_RESTRICTED,
                    ClientState.MULTIPLE_DIFFICULTY : ClientState.MULTIPLE,
                    }[self.GetState()]
        self.SetState(newState)
        self.GetCube().Randomize(difficulty)

    COMMAND_MAP = {
        ClientCommand.WAKE : {
            ClientState.IDLE :              WakeFromIdle,
        },
        ClientCommand.QUIT : {
            ClientState.HOME :              QuitFromHome,
            ClientState.HOME_RESTART :      QuitFromHome,
            ClientState.SINGLE :            QuitFromSingle,
            ClientState.SINGLE_RESTRICTED : QuitFromSingle,
            ClientState.MULTIPLE :          QuitFromMultiple,
        },
        ClientCommand.START_1P : {
            ClientState.HOME :              Start1P,
            ClientState.HOME_RESTART :      Start1P,
        },
        ClientCommand.START_3P : {
            ClientState.HOME :              Start3P,
            ClientState.HOME_RESTART :      Start3P,
        },
        ClientCommand.RESTART : {
            ClientState.SINGLE :            RestartFromSingle,
            ClientState.MULTIPLE :          RestartFromMultiple,
        },
        ClientCommand.SELECT_DIFFICULTY : {
            ClientState.DIFFICULTY :        Scramble,
            ClientState.MULTIPLE_DIFFICULTY : Scramble,
        },
    }

