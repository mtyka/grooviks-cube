import sys
#import uistation;
from uistation import UiStation

#each line in the input file shouls be in the form:
# [COMMAND_ID, BOARD_ID, PIN_POSITION (0-5), [DOWN_PINS, ...] ]  
# By convention:  COMMAND_ID 1-18 are the 9 rotations, in each direction.
#   ROT_ID  = COMMAND_ID / 2;
#   ROT_DIR = COMMAND_ID % 2.
# interesting note... we *have* more inputs than that...  We could map them to different commands, and have those be hidden in the control stations...  *Might be useful to have more inputs...*
#  A command will be considered signaled iff the 'Up is the relevant up, all relevant DOWNs are pressed, and NO additional buttons are pressed
BASEPORT = 23330;

class UIManager:
    def __init__(this):
        lines = [];
        fileName = 'controls.txt';
        for line in file("command_switch.txt"):
            l = eval(line);
            this.command_switch = l[0];
            fileName = l[1];
            
        for line in file( fileName ):
            l = eval(line);
            lines.append(l);

        this.mapping = {};
    
        for l in lines:
            this.mapping[l[1]] = {};
    
        for l in lines:
            if not this.mapping[l[1]].has_key(l[2]):
                this.mapping[l[1]][l[2]] = [];
            this.mapping[l[1]][l[2]].append(l);
            
        this.stations = {};
        for ID in this.mapping:
            PORT = BASEPORT + ID;
            HOST = '';
            this.stations[ID] = UiStation(HOST, PORT);
        
        this.results = {};            
                    
    def broadcast(this, message):
        for STATION_ID in this.stations:
            this.stations[STATION_ID].trySend(message);
        
    def update(this):
        results = [];
        for STATION_ID in this.stations:
            station_results = this.stations[STATION_ID].update();
            if (station_results):
                for result in station_results:
                    UP_PIN = result[0];
                    DOWN_LIST = result[1];
                    if (this.command_switch):
                        possible_matches = this.mapping[STATION_ID][UP_PIN];
                        for possible_match in possible_matches:
                            REQUIRED_DOWN_LIST = possible_match[3];
                            if REQUIRED_DOWN_LIST == DOWN_LIST:
                                COMMAND_ID = possible_match[0];
                                results.append(COMMAND_ID);
                    else:
                        DOWN_LIST.insert(0, UP_PIN);
                        for pin in DOWN_LIST:
                            possible_matches = this.mapping[STATION_ID][pin];
                            for possible_match in possible_matches:
                                COMMAND_ID = possible_match[0];
                                results.append(COMMAND_ID);
                            
                        results.append
                
        #results.sort();
        if (len(results) > 0):
            print results;
            return results;
        return None;
        
        