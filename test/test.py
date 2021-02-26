class Test:

    def __init__(self, locked):
        self.locked = locked

    def getLocked(self):
        print(self.locked)

    def setLocked(self, val):
        self.locked[0] = val

    def doSmtng(self):
        self.setLocked(1)