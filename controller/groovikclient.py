
class GrooviksClient:
    
    def GetCube(self):
        raise "Not implemented; just a reference back to the GroovixCube that owns this client"
    
    def GetState(self):
        raise "Not implemented; return the current ClientState"
    
    def HandleCommand(self, command):
        '''Dispatch to the appropriate handler method for the command'''
        try:
            { 
             ClientCommand.WAKE : HandleCommandWake, 
             ClientCommand.QUIT : HandleCommandQuit,
             ClientCommand.START_1P : HandleCommandStart1P,
             ClientCommand.START_3P : HandleCommandStart3P,
             }[command]()
        except KeyError:
            # TODO: log the failure
            pass

    def HandleCommandWake( self ):
        self.HandleForState({ ClientState.IDLE : WakeFromIdle })

    def HandleCommandQuit( self ):
        self.HandleForState({
                            ClientState.HOME :              QuitFromHome,
                            ClientState.HOME_RESTART :      QuitFromHome,
                            ClientState.SINGLE :            QuitFromSingle,
                            ClientState.SINGLE_RESTRICTED : QuitFromSingle,
                            ClientState.MULTIPLE :          QuitFromMultiple,
                             })
        
    def HandleCommandRestart(self):
        self.HandleForState({
                            ClientState.SINGLE :            RestartFromSingle,
                            ClientState.MULTIPLE :          RestartFromMultiple,
                             })
        
    def HandleCommandStart1P(self):
        self.HandleForState({
                            ClientState.HOME :              Start1P,
                            ClientState.HOME_RESTART :      Start1P,
                            })

    def HandleCommandStart3P(self):
        self.HandleForState({
                            ClientState.HOME :              Start3P,
                            ClientState.HOME_RESTART :      Start3P,
                            })

    def HandleForState( self, actionMap ):
        '''
        Choose the appropriate action for the command, based on the current
        client state.  If there is no mapping for the current state, the 
        command is treated as invalid and ignored.
        '''
        try:
            actionMap[self.GetState()]()
        except KeyError:
            # TODO: log some interesting message
            pass

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
        

