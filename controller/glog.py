import datetime

class GLog:
    def __init__(self, logname):
        self.file = open(logname, 'a')
        
    def logLines(self, lines):
        self.file.writelines(lines)
        self.file.flush()
        
    def logLine(self, line):
        line = str( datetime.datetime.now() ) + " " + line + "\n"
        self.logLines([line])
