extern "C" {
  #include "types.h"
  #include "w5100.h"
  #include "socket.h"
}

// Added WProgram.h so we can use delay() and millis()
//
#include "WProgram.h"

#include "Ethernet.h"
#include "Client.h"
#include "Server.h"

uint16_t Client::_srcport = 0;

Client::Client(uint8_t sock) {
  _sock = sock;
}

// Revisions for construtor
// 1. Initialize _sock to 255 as an indicator that no socket is
//    associated with the client.
//
Client::Client(uint8_t *ip, uint16_t port) {
  _ip = ip;
  _port = port;
  _sock = 255;
}

// Revisions for connect()
// 1. Completely revised the connect() method to rearrange the logic
//    for cleaner flow and to eliminate multiple return points.
// 2. Added a check to see if a socket was already associated with the
//    client and fail the connect if so. This prevents the client from
//    possibly entering an unrecoverable state if another connect() is
//    called without a stop() from a previous connection.
// 3. Revised the available socket search to stop looking when the first
//    available one is found. Previously the code checked all sockets and
//    returned the last available. The change speeds up the code and
//    reduces SPI traffic by not checking unneeded socket statuses.
// 4. Consider a socket in the SOCK_FIN_WAIT state to be available. This
//    is a work-around in case a connection does close cleanly after a
//    stop() (or a remote disconnect). This shouldn't happen anymore
//    with the changes to stop(), but because we have such a limited
//    number of sockets (4) we may have to force the issue or risk
//    getting stuck waiting for dead connection to finish closing.
// 5. Add a check to prevent the _srcport from overflowing into the
//    priviledged port range (0-1023)
// 6. Add a 1ms delay to the loop waiting for the connection to fully
//    establish after a successful connect. This helps prevent excessive
//    SPI traffic as we check the status.
//
uint8_t Client::connect() {
  uint8_t socketStatus;
  uint8_t i=0;
  uint8_t resultCode=0;

  if (_sock == 255) {   

    while ((i < MAX_SOCK_NUM) && (_sock == 255)) {
      socketStatus = getSn_SR(i);
      if ((socketStatus == SOCK_CLOSED) || (socketStatus == SOCK_FIN_WAIT)) {
        _sock = i;
        _srcport++;

        if (_srcport > 64511)  // Prevent overflow of the _srcport into the
          _srcport = 0;        // priviledged range (because of 1024 + _srcport)
    
        socket(_sock, Sn_MR_TCP, 1024 + _srcport, 0);
  
        if (::connect(_sock, _ip, _port)) {
          do {
            socketStatus=getSn_SR(_sock);

// If we haven't connected yet, delay for 1ms so that
// we slow down the excessive SPI traffic
            if (socketStatus != SOCK_ESTABLISHED)
              delay(1);
              
          } while ((socketStatus != SOCK_ESTABLISHED) && (socketStatus != SOCK_CLOSED));
  
          if (socketStatus == SOCK_ESTABLISHED)
            resultCode=1;
        }
      } else
        i++;
    }
    if (resultCode == 0)
      _sock=255;
  }
  return resultCode;
}

// Revisions for write()
// 1. Added a check for a valid socket to prevent a possible
//    array out-of-bounds memory corruption if the method
//    was called when not connected
//
void Client::write(uint8_t b) {
  if (_sock < MAX_SOCK_NUM)     // Valid socket?
    send(_sock, &b, 1);
}

// Revisions for available()
// 1. Added a check for a valid socket to prevent a possible
//    array out-of-bounds memory corruption if the method
//    was called when not connected
//
int Client::available() {
  if (_sock < MAX_SOCK_NUM) {   // Valid socket?
    return getSn_RX_RSR(_sock);
  } else {
    return 0;
  }
}

int Client::read() {
  uint8_t b;
  if (!available())
    return -1;
  recv(_sock, &b, 1);
  return b;
}

void Client::flush() {
  while (available())
    read();
}

// Revisions for stop()
// 1. Completely revised the stop() method to attempt a graceful disconnect
//    instead of a forced close. The original code was doing a close() followed
//    by a diconnect(). If anything, these are in the wrong order. The disconnect()
//    sends a FIN to initiate the connection close. The close() simply shuts down
//    the connection without notifying the remote end. The combination of the two
//    in the reverse order was forcing a connection drop, then sending a FIN. This
//    was causing the connection to get stuck in a SOCK_FIN_WAIT state for about
//    35 seconds (until timeout) waiting for an ACK that won't happen because the
//    connection is already broken.
// 2. Wait up to 1 second (1000ms) for the connection to completely close. If the
//    close times out, force it closed with a close(). The timeout may need
//    adjusting as it's a trade-off between waiting too long and allowing connections
//    to close "nicely" as often as possible.
// 3. Added a check for a valid socket to prevent a possible
//    array out-of-bounds memory corruption if the method
//    was called when not connected
//
void Client::stop() {
  uint8_t disconnectResult = 255;
  unsigned long startTime;
  boolean disconnectDone = false;

  if (_sock < MAX_SOCK_NUM) { // Check added to prevent an out-of-bounds
                              // array corruption if close() is called on
                              // a client that is not connected.
    disconnect(_sock);

// Wait for the connection to close gracefully
    startTime=millis();
    do {
      if (getSn_SR(_sock) == SOCK_CLOSED) {
        disconnectDone=true;
        disconnectResult=millis() - startTime;
      } else if ((millis() - startTime) >= 1000) {  // Timeout
// The delay waiting for the connection to gracefully close
// has expired. Force the connection closed.
        disconnectDone=true;
        close(_sock);
        disconnectResult=255;
      } else {
// If the connection hasn't yet closed, delay for 1ms so that
// we slow down the excessive SPI traffic
        delay(1);
      }
    } while (! disconnectDone);

    EthernetClass::_server_port[_sock] = 0;
    _sock = 255;   // Indicate that no socket is in use
  }
}


// Revisions for connected()
// 1. Added state SOCK_FIN_WAIT to the list of disconnected states. If we're
//    going to allow sockets in this state to be available for connect(),
//    the we need to also consider them not connected.
//
uint8_t Client::connected() {
  uint8_t s = status();
  return !(s == SOCK_LISTEN || s == SOCK_CLOSED || (s == SOCK_CLOSE_WAIT && !available()) || (s == SOCK_FIN_WAIT));
}

uint8_t Client::status() {
  return getSn_SR(_sock);
}

// the next three functions are a hack so we can compare the client returned
// by Server::available() to null, or use it as the condition in an
// if-statement.  this lets us stay compatible with the Processing network
// library.

uint8_t Client::operator==(int p) {
  return _sock == 255;
}

uint8_t Client::operator!=(int p) {
  return _sock != 255;
}

Client::operator bool() {
  return _sock != 255;
}
