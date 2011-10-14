#include <Ethernet2.h>
#include <stdio.h>

// Configurable parameters.
#define STATION_ID  2
#define BASE_PORT 23330
long DEBOUNCE_MILLIS = 50;
long MIN_PRESS_INTERVAL_MILLIS = 0; // XXX
byte serverIp[] = {10, 0, 0, 1};

// Debugging foo.
#define SERIAL_DEBUG 1
#define DEBUGPRINT(str) {if (SERIAL_DEBUG) Serial.println(str);}

// Button hardware state
long RELEASED = LOW;
long PRESSED  = HIGH;
long UNKNOWN = 1000;
int numButtons = 6;
int buttonPins[6] = {2, 3, 4, 5, 6, 7};

// Output settings & variables
#define OUTPUT_STRING_LENGTH (80) // XXX 25
char outputString[OUTPUT_STRING_LENGTH] = "";
long lastMsgSentTime;

// Server (ethernet) variables
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xE0 + STATION_ID };
byte ourIp[] = { 10, 0, 0, 200+STATION_ID };
#define STATION_PORT (BASE_PORT + STATION_ID)
boolean waitingForConnection;
long lastTryToConnectTime;
Client client(serverIp, STATION_PORT);

// Lock hardware & variables
#define AUTO_UNLOCK_TIME_MILLIS 10000
boolean locked;
long lastLockedTime;

// LED variables
long LED_ON = HIGH;
long LED_OFF = LOW;
long FLASH_INTERVAL = 1000;
long lastFlashedTime;
int ledPin = 9;
int ledState;

#define NONE 0
#define CLEARING 1
#define UP 2
#define DEBOUNCE_DOWN 3
#define DOWN 4
#define DEBOUNCE_UP 5

#define PRESSED 0
#define RELEASED 1
#define UNKNOWN 3
typedef int ButtonStateType;
typedef int ButtonValueType; 

boolean do_print = true;

struct Button {
    int pin_;
    ButtonStateType state_;
    long stateEntryTime_;
    boolean noMsg_;
    long downStateEntryTime_;
    
    Button() {
      pin_ = -1;
      state_ = CLEARING;
      stateEntryTime_ = 0;
      downStateEntryTime_ = 0;
      noMsg_ = false;
    }

    void setPin(int pin) {
      pin_ = pin;
     pinMode(pin, INPUT);
    }      
    
    void print() {
      return;
      snprintf(outputString, OUTPUT_STRING_LENGTH -1, "P:%d  S:%d  ST:%d  DST: %d  NM: %d", pin_, state_, stateEntryTime_, downStateEntryTime_, noMsg_);
      DEBUGPRINT(outputString);
    }
   
   ButtonStateType getCurrentState() {
      return state_;
   }
   
   void suppressMessage() {
       noMsg_ = true;
   }
   
   long getDownStateEntryTime() {
       return downStateEntryTime_;
   }
   
   void reset() {
       state_ = CLEARING;
   }
  
   ButtonStateType updateState(ButtonValueType curValue, long now) {
      switch (state_) {
       case NONE:
           return CLEARING;
       case CLEARING:
           if (curValue == RELEASED) {
              return UP;
           }  
           break;
       case UP:
           downStateEntryTime_ = 0;
           noMsg_ = false;
           if (curValue == PRESSED) {
             return DEBOUNCE_DOWN;
           }
           break;
       case DEBOUNCE_DOWN:
           if (curValue == PRESSED) {
               if (now - stateEntryTime_ > DEBOUNCE_MILLIS) {
                   return DOWN;
               }
           } else if (curValue == RELEASED) {  
               return UP;
           }
          break;
       case DOWN:
         if (downStateEntryTime_ == 0) {
             downStateEntryTime_ = now;
         }
          if (curValue == RELEASED) {
             return DEBOUNCE_UP;
          }
          break;
       case DEBOUNCE_UP:
          if (curValue == RELEASED) {
             if (now - stateEntryTime_ > DEBOUNCE_MILLIS) {
                 return UP;
             }
          } else if (curValue == PRESSED) {
            return DOWN;
          }
          break;
       default:
          break;
      }
      return state_;
   }

   ButtonValueType readPin() {
     long pinValue =  digitalRead(pin_);
     if (pinValue == HIGH) {
         return PRESSED;
     } else if (pinValue == LOW) {
         return RELEASED;
     } else {
         return UNKNOWN;
     }
   }
   
   boolean update(long now) {
      ButtonValueType pinValue = readPin();
      ButtonStateType newState = updateState(pinValue, now);
      boolean sendMsg = false;
      if (newState == UP && state_ == DEBOUNCE_UP && !(noMsg_ == true)) {
          // Send a message!
          sendMsg = true;
      }
      if (newState != state_) {
          stateEntryTime_ = now;
          do_print = true; // DEBUG: Makes print on anystate change
      }
      state_ = newState;
      return sendMsg;
   }
};
 
Button buttons[6];

// ************* Ethernet*************

boolean updateConnection() {
  long now = millis();
  if (waitingForConnection && (now - lastTryToConnectTime > 5000)) {
    lastTryToConnectTime = now;
    DEBUGPRINT("Trying to connect...");
    waitingForConnection = !client.connect();
    if (!waitingForConnection) {
      DEBUGPRINT("Connect, ted");
    }
  }
  if (!waitingForConnection && client.connected()) {
    if (now - lastMsgSentTime> 5000) {
      client.print("Alive\n");
      lastMsgSentTime = now;
    }
  } else {
     if (!waitingForConnection) {
        DEBUGPRINT("Disconnect, Ting."); 
       client.stop(); 
       waitingForConnection = true;
     }
  }
 return !waitingForConnection; 
}


// ************* Ethernet : Receiving *************
char getLastTransmittedChar() { 
   char result = -1;
   char lastValidChar = -1;
   char lastChar = -1;

   while (!waitingForConnection && client.connected() && client.available()) {       
      lastChar = client.read();
      if (lastChar != -1 && (lastChar == 'U' || lastChar == 'L')) {
        lastValidChar = lastChar;
      }
   }
   return lastValidChar;
}


// ************* Ethernet : Sending *************
void sendMessage(char *msg, long now) {
  if (!waitingForConnection && client.connected() && now - lastMsgSentTime > MIN_PRESS_INTERVAL_MILLIS) {
     lastMsgSentTime = millis();
     client.print(msg);
  }
}


void generateMessage(char *msg, int sendMsgMask) {
    int earliestDownButtonThatIsNowUp = -1;
    for (int i = 0; i < numButtons; ++i) {
       if ( (1 << i) & sendMsgMask )
       {
           earliestDownButtonThatIsNowUp = i;
           break;
       }
    }
     //buttons[i].getCurrentState() == UP) { /// BUG BUG BUG
     //      if (earliestDownButtonThatIsNowUp == -1  || 
     //          buttons[i].getDownStateEntryTime() < buttons[earliestDownButtonThatIsNowUp].getDownStateEntryTime()) {
     //          earliestDownButtonThatIsNowUp = i;
     //      }
     //  }
     // }
    if (earliestDownButtonThatIsNowUp == -1)
      return;
    
    DEBUGPRINT("Hit!\n"); 
        snprintf(msg, OUTPUT_STRING_LENGTH, "U%d\n", earliestDownButtonThatIsNowUp);
    int numButtonsPressed = 1;
    for (int i = 0; i< numButtons; ++i) {
        if (i == earliestDownButtonThatIsNowUp) {
          continue;
        }
        int foo = 0;
        ButtonStateType state = buttons[i].getCurrentState();
        if (((1 << i) & sendMsgMask) || state == DEBOUNCE_UP || state == DOWN) {
            snprintf(msg + 2*numButtonsPressed, OUTPUT_STRING_LENGTH - 2*numButtonsPressed, "D%d\n",
                     i);
            numButtonsPressed++;
        }
    }       
 DEBUGPRINT(msg); 
}

// ************* Ethernet : Update Locked / LEDs.  *************
boolean updateLocked(long now, char c) {
   boolean oldLocked = locked;
   if ((now - lastLockedTime > AUTO_UNLOCK_TIME_MILLIS) || (c == 'U')) {
       locked = false;
       lastLockedTime = 0;
   }
   if (c == 'L') {
       locked = true;
       lastLockedTime = now;
   }
   return oldLocked;
}
   
void updateLeds(boolean flash, boolean locked, long now) {
    if (flash) {
        if (now - lastFlashedTime > FLASH_INTERVAL) {
          if (ledState == LED_OFF) {
              ledState = LED_ON;
          } else {
              ledState = LED_OFF;
          }
          lastFlashedTime = now; 

        }
    } else if (locked) {
      ledState = LED_OFF;
    } else {
      ledState = LED_ON;
    }
    digitalWrite(ledPin, ledState);
}
    


// ************* Initialization *************
void setup() {
  Ethernet.begin(mac, ourIp);
  Serial.begin(9600);
  lastMsgSentTime = millis();
  waitingForConnection = true;
  lastTryToConnectTime = 0;
  
  pinMode(ledPin, OUTPUT);
  locked = false;
  lastLockedTime = 0;
  ledState = LED_OFF;
  lastFlashedTime = 0;
  
  for (int i = 0; i < numButtons; ++i) {
    buttons[i].setPin(buttonPins[i]);
  }
}



// ************* LOOP *************
void loop()
{  
   // Brother A-to-Z, what TIME is it?
   long now = millis();
   
   // Manange connection.
   updateConnection();
   
   // Handle locked state changes.
   char lastChar = getLastTransmittedChar();
   int oldLocked = updateLocked(now, lastChar);
   if (oldLocked == true && locked == false) {
     for (int i = 0; i< numButtons; ++i) {
       buttons[i].reset();
     }
   }
   
   // Manage the LEDs
   updateLeds(waitingForConnection, locked, now);
   
   // Update Buttons
   int sendMsgMask = 0;
   for (int i = 0; i< numButtons; ++i) {
     sendMsgMask |= ((buttons[i].update(now) ? 1 : 0) << i);
   }
   if (sendMsgMask != 0) 
   {
       generateMessage(outputString, sendMsgMask);
       if (!locked) 
       {
         sendMessage(outputString, now);
       }
       for (int i = 0; i< numButtons; ++i) 
       { 
         buttons[i].suppressMessage();       
       }
   }
   
   if (do_print) {
     // **** DEBUG PRINT ALL STATE **** /
          for (int i = 0; i<numButtons; ++i) {
            buttons[i].print();
          }
   }
   do_print = false;
   // Take a brief breath.
   delay(10);
}

