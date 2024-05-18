import random

class Game:
    def __init__(self, players, copies, starting_player):
        self.players = players
        self.card_copies = copies
        self.turn_index = starting_player
        
        self.indexes_board = []
        self.current_player = self.players[self.turn_index]
        self.last_id = None
        self.last_image_id = None
        self.create_index_board()
        
    def create_index_board(self):
        board = list(range(0, self.card_copies)) * 2
        
        #Swap indexes randomly
        for _ in range(30):
            x, y = random.randrange(0, len(board)-1), random.randrange(0, len(board)-1)
            swapper = board[x]
            board[x] = board[y]
            board[y] = swapper
            
        self.indexes_board = board
    
    def change_turn(self):
        if self.turn_index + 1 <= len(self.players) - 1: self.turn_index += 1
        else: self.turn_index = 0
        
        self.current_player = self.players[self.turn_index]
        
    def check_game_over(self):
        total_matches = 0
        for player in self.players: total_matches += player.matches
            
        return total_matches == self.card_copies
    
    def create_leaderboard(self):
        for i in range(0, len(self.players)):
            for j in range(i+1, len(self.players)):
                if self.players[i].matches < self.players[j].matches: 
                    swapper = self.players[i]
                    self.players[i] = self.players[j]
                    self.players[j] = swapper
                    
        leaderboard = [
            [str(i+1), self.players[i].username, str(self.players[i].matches)]
            for i in range(len(self.players))
        ] 
        
        return leaderboard