class Player:
    def __init__(self, socket):
        self.socket = socket
        
        self.username = ""
        self.matches = 0
        self.moves = 2
    
    def move(self):
        if self.moves - 1 > 0: 
            self.moves -= 1
            return True
        else: 
            self.moves = 2
            return False