class KeyHandler():
    def __init__(self, key):
        self.handled = False
        self.key = key


    def onKeyDown(self):
        pass

    def onKeyUp(self):
        self.handled = False


    def isClicked(self):
        if self.handled == False:           
            self.handled = True
            return True
        elif self.handled == True:
            return False