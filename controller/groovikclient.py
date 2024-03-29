
from hbclient import *
from groovikutils import *
import groovik
from time import time

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
        
    def GetStart1PRequestTime(self):
        '''Return the time that this session requested a single player game'''
        return self.__singleRequestTime
    
    def HandleCommand(self, command, parameters):
        '''
        Choose the appropriate action for the command, based on the current
        client state.  If there is no mapping for the current state, the 
        command is treated as invalid and ignored.
        '''
        actionMap = GrooviksClient.COMMAND_MAP[command]
        try:
            action = actionMap[self.GetState()]
        except KeyError:
            self.LogEvent("Cannot execute command %s in state %s" % (command, self.GetState()))
            return
            
        self.LogEvent("Exceuting command %s in client state %s; game state is %s" % (command, self.GetState(), self.GetCube().GetGameState()))
        try:
            action(self, parameters)
            self.LogEvent("Command complete.  New client state is %s; game state is %s; active position is %s" % (self.GetState(), self.GetCube().GetGameState(), self.GetCube().GetActivePosition()))
        except Exception as e:
            self.LogEvent("Command %s failed: %s" % (command, e.args))
            raise e

    #--------------------------------------------------------------
    # Actions
    #--------------------------------------------------------------
    def WakeFromIdle( self, parameters ):
        newState = {
                    GameState.UNBOUND :             ClientState.HOME,
                    GameState.SINGLE :              ClientState.HOME,
                    GameState.SINGLE_INVITE :       ClientState.MULT,
                    GameState.MULTIPLE :            ClientState.MULT,
                    GameState.VICTORY :             ClientState.HOME,
                    }[self.GetCube().GetGameState()]
        self.SetState(newState)

    def QuitFromHome(self, parameters):
        self.SetState(ClientState.IDLE)

    def QuitFromSingle(self, parameters):
        self.SetState(ClientState.IDLE)
        self.GetCube().SinglePlayerExits(self)
        
    def QuitFromMultiple(self, parameters):
        self.SetState(ClientState.IDLE)
        self.GetCube().MultiplePlayerExits()
        
    def RestartFromSingle(self, parameters):
        raise NotImplementedError()
        
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
        raise NotImplementedError()
        
    # TODO: it looks like Start1P and Start3P should probably be factored
    def Start1P(self, parameters):
        self.SetState(ClientState.SING)
        self.__singleRequestTime = time()
        self.GetCube().SinglePlayerStarts(self)

    def Start3P(self, parameters):
        self.SetState(ClientState.MULT)
        self.GetCube().MultiplePlayerStarts()
        
    def Join3P(self, parameters):
        self.SetState(ClientState.MULT)
        self.GetCube().SinglePlayerJoins(self)

    def Scramble(self, parameters):
        difficulty = parameters['difficulty']
        self.GetCube().Randomize(self, difficulty)

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
        ClientCommand.JOIN_3P : {
            ClientState.SING :              Join3P,
        },
        ClientCommand.SELECT_DIFFICULTY : {
            ClientState.SING :        Scramble,
            ClientState.MULT :                 Scramble,
        },
    }

