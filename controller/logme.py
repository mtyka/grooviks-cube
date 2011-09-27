import time;

def timestamp():
	return time.ctime(time.time())

def logme( m, m2="", m3="", m4="", m5="", m6="" ):
  print '[', timestamp() ,']',m,m2,m3,m4,m5,m6	
