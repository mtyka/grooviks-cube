#include <Ethernet2.h>
#include <stdio.h>

// Configurable parameters.
#define STATION_ID  1
#define BASE_PORT 23330
long DEBOUNCE_MILLIS = 50;
long MIN_PRESS_INTERVAL_MILLIS = 500;
//byte serverIp[] = {10, 0, 0, 1};
byte serverIp[] = {10, 0, 0, 1};


#define SERIAL_DEBUG 1
#define DEBUGPRINT(str) {if (SERIAL_DEBUG) Serial.println(str);}

// Switch variables
int numSwitches = 6;
int switchPins[6] = {2, 3, 4, 5, 6, 7};
int switchState[6] = {0, 0, 0, 0, 0, 0};
long changeStartTime[6] = {-1, -1, -1, -1, -1, -1};
long lastPressedTime[6];
long NO_CHANGE = -1;
long RELEASED = LOW;
long PRESSED  = HIGH;

// Output variables
#define OUTPUT_STRING_LENGTH (25)
char outputString[OUTPUT_STRING_LENGTH] = "";
long lastSentTime[6];

// Server variables
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xE0 + STATION_ID };
byte ourIp[] = { 10, 0, 0, 200+STATION_ID };
long lastTryToConnectTime;
long lastMsgSentTime;
boolean waitingForConnection;
#define STATION_PORT (BASE_PORT + STATION_ID)
Client client(serverIp, STATION_PORT);

void setup()
{
  Ethernet.begin(mac, ourIp);
  Serial.begin(9600);
  lastMsgSentTime = millis();
  waitingForConnection = true;
  lastTryToConnectTime = 0;
  
  long now = millis();
  for (int i = 0; i < numSwitches; ++i) {
     pinMode(switchPins[i], INPUT);
    lastPressedTime[i] = 0;
    lastSentTime[i] = 0;
  }

}

boolean updateSwitch(int i) {
  long now = millis();
  int curState = digitalRead(switchPins[i]);
  if (curState == switchState[i]) {
    changeStartTime[i] = NO_CHANGE;
    return false;
  }
  if (changeStartTime[i] == NO_CHANGE) {
    changeStartTime[i]= now;
    return false;
  }
  if (now - changeStartTime[i] > DEBOUNCE_MILLIS) {
    switchState[i] = curState;
    if (curState == PRESSED)  {
      lastPressedTime[i] = changeStartTime[i];
    }
    changeStartTime[i] = NO_CHANGE;
    return true;
  }
  return false;
}



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

void sendMessage(char *msg) {
  if (!waitingForConnection && client.connected()) {
     lastMsgSentTime = millis();
     client.print(msg);
  }
}

void loop()
{  
   updateConnection();
   for (int i = 0; i< numSwitches; ++i) {
     if (updateSwitch(i)) {
         long now = millis();
         if (switchState[i] == PRESSED &&  
             now - lastSentTime[i] >MIN_PRESS_INTERVAL_MILLIS) {
           DEBUGPRINT("Hit!"); 
           snprintf(outputString, OUTPUT_STRING_LENGTH, "P%d\n", i);
           sendMessage(outputString);
           lastSentTime[i] = now;
         }
     }
   }
   delay(10);
}

