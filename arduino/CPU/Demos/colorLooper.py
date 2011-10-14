
class colorLooper:
    def __init__(self):
        self.cur_r = 0
        self.cur_g = 0
        self.cur_b = 0
        self.crange = 5

    def incColor(self, c):
        return (c + 1) % self.crange

    def gotoNextColor(self):
        self.cur_r = self.incColor(self.cur_r)
        if (self.cur_r > 0):
            return
        self.cur_g = self.incColor(self.cur_g)
        if (self.cur_g > 0):
            return
        self.cur_b = self.incColor(self.cur_b)

    def incBlue(self ):
        self.cur_b = self.incColor(self.cur_b)
        
    def scaleColor(self, c):
        if (c == 0):
            return c
        return (c * (256/self.crange))-1

    def getColorString(self, i):
        r1 = self.scaleColor(self.cur_r)
        g1 = self.scaleColor(self.cur_g)
        b1 = self.scaleColor(self.cur_b)
        print "S: ", r1,g1,b1
        return "%c%c%c%c%c" % (0,i,r1,g1,b1)

    def setColors(self, r, g, b):
        self.cur_r = r
        self.cur_g = g
        self.cur_b = b
