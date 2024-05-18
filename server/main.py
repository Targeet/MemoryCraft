import time, random, pickle, settings
from classes.player import Player
from classes.game import Game
from threading import Thread
from socket import *

###
# VARIABLES
###

#Address
SERVER_PORT = 14810
SERVER_IP = gethostbyname(gethostname())
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

#Create socket
SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
SERVER_SOCKET.bind(SERVER_ADDR)
SERVER_SOCKET.listen(1)

#Game const
MIN_PLAYERS = settings.data["min_players"]
MAX_PLAYERS = settings.data["max_players"]
WAIT_TIME = settings.data["lobby_wait_time"]
CARD_COPIES = 8 

#Game vars
players = []
lobby = [] #Players waiting for a game
games = []

###
# FUNCTIONS
###

#Utils
def wait(mills):
    time.sleep(mills / 1000) 

#Communication
def connection_handler(player): #Listen to client messages
    players.append(player)
    try:
        while True:
            message = pickle.loads(player.socket.recv(1024))
            
            #Create a thread to handle the message processing
            Thread(target = process_message, args = (message, player,)).start()

    except Exception as ex:
        if str(ex).__contains__("[WinError 10054]"): #When a client disconnects
            print(str(player.socket.getsockname()) + " disconnected from the server.")
            
            players.pop(players.index(player))
            player.socket.close()
            
            if player in lobby: process_message(["leave_lobby", None], player)
            else:
                for game in games:
                    if player in game.players:
                        game.players.pop(game.players.index(player))
                        if len(game.players) <= 1: end_game(game)
                        break
        else: print(ex)
def send_message(message, clients): #Send a message to a list of clients
    for client in clients: 
        client.socket.send(pickle.dumps(message))
        
    print(message)
    wait(40) #Give time to clients to proccess the message
def process_message(message, sender): #Filter the message
    service = message[0]
    data = message[1]
    
    match service:
        case "enter_lobby": #Player joins the lobby
            players[players.index(sender)].username = data
            lobby.append(sender)
            
            update_lobby_interface()
            
            if len(lobby) == MAX_PLAYERS: start_game()
            elif len(lobby) == MIN_PLAYERS: Thread(target=lobby_timer, args=()).start()
        case "leave_lobby": #When a player disconnects while waiting in lobby
            lobby.pop(lobby.index(sender))
            
            update_lobby_interface()
        case "flip_card": 
            id = data[0] #Position in the board
            image_id = data[1] #Image index
            
            #Find sender's game
            current_game = None
            for game in games:
                if sender in game.players:
                    current_game = game
            
            #Save last flipped card  id's
            if current_game.last_image_id == None:
                current_game.last_image_id = image_id
                current_game.last_id = id
            
            #List of players to send the message
            list = current_game.players.copy()
            list.pop(list.index(sender))
            send_message(["flip_card", id], list)
            
            #Check if the player flipped 2 cards
            if not sender.move():
                send_message(["turn", False], current_game.players)
                
                matched = (image_id == current_game.last_image_id)
                
                wait(300) #Wait for the flip
                
                if matched: send_message(["matched", True], [current_game.current_player])
                else: send_message(["matched", False], [current_game.current_player])
                
                wait(1200) #Time to memorize cards
                
                if matched: #Cards match
                    sender.matches += 1
                    
                    if current_game.check_game_over(): 
                        end_game(current_game)
                        return
                else: #Cards do not match
                    #Flip both cards back
                    send_message(["flip_card", id], current_game.players)
                    send_message(["flip_card", current_game.last_id], current_game.players)
                    
                    #Change turn
                    current_game.change_turn()
                
                send_message(["turn", True], [current_game.current_player])
                
                #Reset id's
                current_game.last_image_id = None
                current_game.last_id = None

#Game
def end_game(game):
    #Update game state and send leaderboard to all players
    send_message(["update_game_state", False], game.players)
    send_message(["leaderboard", game.create_leaderboard()], game.players)
    for i, player in enumerate(game.players):
        send_message(["position", i + 1], [player])

    #Remove the game
    global games
    games.pop(games.index(game))
def start_game(): 
    global lobby
    global games
    send_message(["update_message", "Game Starting!"], lobby)
    wait(2000)
    send_message(["update_game_state", True], lobby)
    
    #Create game and the board
    games.append(Game(lobby, CARD_COPIES, random.randint(0, len(lobby)-1)))
    
    #Send the board to all players
    send_message(["board_indexes", games[-1].indexes_board], games[-1].players)
    
    #Starting turn
    send_message(["turn", False], games[-1].players)
    send_message(["turn", True], [games[-1].current_player])
    
    lobby = [] #.clear() causes problems?? why tf
def update_lobby_interface(): 
    if len(lobby) == 1: send_message(["update_message", "Waiting For Players..."], lobby)

    usernames = [player.username for player in lobby]
    
    send_message(["update_nplayers", f"{len(lobby)}/{MAX_PLAYERS}"], lobby)
    send_message(["update_usernames", usernames], lobby)
def lobby_timer(): #Timer to wait for the game to start 
    for i in range(WAIT_TIME + 1):
        wait(1000)
        send_message(["update_message", f"Game Starts In {WAIT_TIME - (i)} Seconds"], lobby)
        
        #Stop timer
        if len(lobby) < MIN_PLAYERS or len(lobby) == MAX_PLAYERS: return
    start_game()

###
# MAIN
###

def main():
    print(f"Server started on: {SERVER_ADDR}")
    while True:
        connection_socket, client_address = SERVER_SOCKET.accept()
        
        print(f"{client_address} connected to the server.")
        
        Thread(target = connection_handler,args = (Player(connection_socket),)).start()

if __name__ == "__main__":
    main()