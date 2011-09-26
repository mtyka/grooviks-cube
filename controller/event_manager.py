#!/usr/bin/env python

import SimpleXMLRPCServer
import xmlrpclib
import threading
import traceback
import time
from logme import logme

debug = False
log = False
"""
subclass this class to receive events from the cube
"""
class CubeEventListener(object):      
   def __init__(self):
      pass
   def connect(self):
      pass
   def disconnect(self):
      pass
   def rotate(self, axis, rows, directions, length):
      pass
   def reward(self, level):
      pass
   def punish(self, level):
      pass
   def set_solve_level(self, state):
      pass
   def invalid_move(self, axis):
      pass
   def idle(self, type):
      pass
"""
Kicks off a thread that listens for cube events
"""
def connect_cube_event_listener(event_listener,
                                local_addr, local_port,
                                remote_addr, remote_port):
      """
      reregister every second, to make sure we're always connected
      """
      def register_loop(event_listener, local_addr, local_port, remote_addr, remote_port):
         server = None
         okay = False
         while (True):
            try:
               if not okay:
                  server = xmlrpclib.ServerProxy("http://{0}:{1}".format(remote_addr, remote_port), allow_none = True)
                  event_listener.set_solve_level(server.get_solve_level())
                  event_listener.connect()
               server.register_client(local_addr, local_port)
               okay = True
            except:
               if debug:
                  traceback.print_exc()
               if okay:
                  event_listener.disconnect()
               okay = False
            time.sleep(1)
         
      def cube_connect_loop(event_listener, local_addr, local_port):
         server = SimpleXMLRPCServer.SimpleXMLRPCServer((local_addr, local_port), allow_none = True, logRequests = debug)
         server.register_instance(event_listener)
         
         try:
            server.serve_forever()
         except:
            if debug:
               traceback.print_exc()
               
      reg_thread = threading.Thread(target = register_loop, args=[event_listener, local_addr, local_port, remote_addr, remote_port])
      reg_thread.daemon = True
      reg_thread.start()
   
      server_thread = threading.Thread(target = cube_connect_loop, args = [event_listener, local_addr, local_port])
      server_thread.daemon = True # die when the main loop exits
      server_thread.start()
      if log:
         print("client: started at {0}:{1}".format(local_addr, local_port))
         


class CubeEventManagerServer(object):
   def __init__(self, em):
      self.__em = em
   
   def register_client(self, client_addr, client_port):
      self.__em.add_client(client_addr, client_port)
      
   def unregister_client(self, client_addr, client_port):
      self.__em.remove_client(client_addr, client_port)
      
   def get_solve_level(self):
      return self.__em.solve_level
   
   def ping(self):
      return

class CubeEventManager(object):
   def __init__(self, solve_level):
      self.__server_addr = "0.0.0.0"
      self.__server_port = 64005 # make configurable
      self.__clients = {}
      self.__solve_level = solve_level
      self.__ems = CubeEventManagerServer(self)
      self.__server = SimpleXMLRPCServer.SimpleXMLRPCServer((self.__server_addr, self.__server_port), allow_none = True, logRequests = debug)
      self.__server.register_instance(self.__ems)
      self.__server_thread = threading.Thread(target = self.__server.serve_forever)
      self.__server_thread.daemon = True # die when the main loop exits
      self.__server_thread.start()
      
      if log:
         print("server:starting at {0}:{1}".format(self.__server_addr, self.__server_port))
      
   @property
   def solve_level(self):
      return self.__solve_level
       
   def __get_client(self, client_addr, client_port):
      return "http://{0}:{1}".format(client_addr, client_port)
      
   def add_client(self, client_addr, client_port):
      client = self.__get_client(client_addr, client_port)
      if (self.__clients.has_key(client)):
         return
      if log:
         print("server:client {0}:{1} added".format(client_addr, client_port))
      self.__clients[client] = xmlrpclib.ServerProxy(client, allow_none = True)
      
   def remove_client(self, client_addr, client_port):
      if log:
         print("server:client {0}:{1} removed!".format(client_addr, client_port))
      client = self.__get_client(client_addr, client_port)
      del self.__clients[client]
      
   """
   Axis is 0-2
   Row is a list of (0-2), indicating which axises have been rotated
   Direction is a list of 0-1 (forwards/backwards)
   """
   def rotate(self, axis, rows, directions, length):
      self.__call_clients("rotate", axis, rows, directions, length)
   
   """
   level should be 0-15 with 15 being the bestest/worstest
   level 15 reward is victory
   """
   def reward(self, level):
      self.__call_clients("reward", level)
      
   def punish(self, level):
      self.__call_clients("punish", level)
   
   """
   state should be 0-15 with 15 being the most solved
   """
   def set_solve_level(self, level):
      self.__solve_level = level
      self.__call_clients("set_solve_level", level)
   
   """
   axis should be 0-2
   """
   def invalid_move(self, axis):
      self.__call_clients("invalid_move", axis)

   """
   type should be 0-4
   """
   def idle(self, type):
      self.__call_clients("idle", type)

   """
   Calls the named function on all the clients. If there is an exception,
   the client is removed from future calls.
   """
   def __call_clients(self, func, *args):
      def call_func(self, func, args):
         del_clients = []
         for client in self.__clients.items():
            try:
               getattr(client[1], func)(*args)
            except:
               if debug:
                  traceback.print_exc()
               del_clients.append(self.__clients[client[0]])
               
         for dc in del_clients:
            try:
               if log:
                  print("server:client {0} removed!".format(client[0]))
               del self.__clients[client[0]]
            except:
               continue
      t = threading.Thread(target = call_func, args = [self, func, args])
      t.daemon = True
      t.start()
         
"""
Test
"""
class TestCubeEventListener(CubeEventListener):      
   def __init__(self):
      pass
   def rotate(self, axis, rows, directions, length):
      print("rotate, axis: {0}, rows: {1}, directions: {2}, length: {3}".format(axis, rows, directions, length))
   def reward(self, level):
      print("reward, level {0}".format(level))
   def punish(self, level):
      print("punish, level {0}".format(level))
   def set_solve_level(self, level):
      print("set_solve_level, level {0}".format(level))
   def invalid_move(self, axis):
      print("invalid_move, level {0}".format(axis))
   def idle(self, type):
      print("idle, state {0}".format(type))

if __name__ == "__main__":
   import sys
   
   def usage():
      print('Please specify either "client" or "server"')
      sys.exit(-1)
      
   if (len(sys.argv) < 2):
      usage()
   if (sys.argv[1] == "client"):
      logme( "Connecting 2 clients" )
      #connect_cube_event_listener(TestCubeEventListener(), "0.0.0.0", 65005, "localhost", 64005)
      connect_cube_event_listener(TestCubeEventListener(), "10.0.0.2", 65001, "10.0.0.1", 64005)
      inp = raw_input("Hit return to stop listening.")
         
   elif (sys.argv[1] == "server"):
      def serve_loop(em):
         s = 0
         while(True):
            em.set_solve_level(s)
            em.rotate(0, [1,2], 1, .5)
            em.invalid_move(1)
            em.reward(3)
            em.punish(4)
            em.idle(5)
            time.sleep(2)
            s = s+1
      em = CubeEventManager(5)
      t = threading.Thread(target = serve_loop, args=[em])
      t.daemon = True
      t.start()
      inp = raw_input("Hit return to stop serving.")
      
   else:
      usage()
      
