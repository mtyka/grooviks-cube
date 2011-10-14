import socket
import time

class UiStation: 
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.connected = False;
        self.lastDataTime = time.time()
        self.lastTryConnectTime = 0
        self.debug = True

    def debugprint(self, str):
        if (self.debug):
            print str

    def tryConnect(self):
        result = False
        self.s.listen(1)
        self.s.setblocking(False)
        result = False;
        try:
            self.conn, addr = self.s.accept()
            print 'Connected by ', addr
            self.conn.setblocking(False)
            self.lastDataTime = time.time()
            result = True
        except socket.error, msg:
            self.debugprint(msg)
            pass
        return result;

    def disconnect(self):
        print "Closing connection nicely"
        self.conn.close()

    def tryRead(self):
        result = None
        try:
            result =  self.conn.recv(1024)
        except socket.error, msg:
            pass
        return result;

    def connected(self):
        return self.connected

    def update(self):
        # Try to connect. Bail on failure.
        if (not self.connected and 
            time.time() - self.lastTryConnectTime > 3.0):
            self.connected = self.tryConnect();
            self.lastTryConnectTime = time.time()
        if (not self.connected):
            return None

        # Try to read.
        data = self.tryRead();
        if (data == None or len(data) == 0):
            if (time.time() - self.lastDataTime  > 10.0):
                print "Connection timed out."
                self.disconnect()
                self.connected = False
        else:
            new_data = self.tryRead()
            while new_data != None and len(new_data) > 0:
                data += new_data
                new_data = self.tryRead()
            self.lastDataTime = time.time()
            msgs = data.splitlines()
            result = []
            for msg in msgs:
                if (len(msg) < 2):
                    continue
                if (msg[0] == 'P'):
                    result.append(ord(msg[1]) - ord('0'))
            result = list(set(result))
            result.sort()
            if (len(result) > 0):
                return result
        return None
