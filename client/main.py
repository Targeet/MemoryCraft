import pygame, sys, math, pickle, time, random, settings
from classes.textbox import TextBox
from classes.button import Button
from classes.image import Image
from classes.label import Label
from classes.card import Card
from threading import Thread
from socket import *
pygame.mixer.init()
pygame.init()

###
# SETTINGS
###

ASSETS_PATH = settings.ASSETS_PATH
VOL = settings.data["volume"]
SERVER_SEARCH_TIME = settings.data["server_max_search_time"]
FPS = settings.data["max_fps"]

###
# FUNCTIONS
###

#Utils
def create_font(size): #Create a font object
    return pygame.font.Font(FONT_PATH, size)
def draw_background(image): #Draw an image on the screen
    WINDOW.blit(image, (0,0))

#Communication
def next_ip(ip):
    new_ip = ip
    split = ip.split('.')
    
    a,b,c,d = int(split[0]), int(split[1]), int(split[2]), int(split[3])
    if d + 1 < 254: new_ip = f"{a}.{b}.{c}.{d + 1}"
    else:
        if c + 1 < 255: new_ip = f"{a}.{b}.{c + 1}.{1}"
        else: 
            if b + 1 < 255: new_ip = f"{a}.{b + 1}.{0}.{1}"
            else:
                if a + 1 < 255: new_ip = f"{a + 1}.{0}.{0}.{1}"
                else: 
                    return new_ip
    
    return new_ip
def previous_ip(ip):
    new_ip = ip
    split = ip.split('.')
    
    a,b,c,d = int(split[0]), int(split[1]), int(split[2]), int(split[3])
    if d - 1 >= 1: new_ip = f"{a}.{b}.{c}.{d - 1}"
    else:
        if c - 1 >= 0: new_ip = f"{a}.{b}.{c - 1}.{254}"
        else: 
            if b - 1 >= 0: new_ip = f"{a}.{b - 1}.{255}.{254}"
            else:
                if a - 1 >= 0: new_ip = f"{a - 1}.{255}.{255}.{254}"
                else: 
                    return new_ip

    return new_ip
def search_server(start_ip, port):
    setdefaulttimeout(0.02)
    start_time = time.time()
    port = port
    ip_next = start_ip
    ip_previous = start_ip
    
    s = socket(AF_INET, SOCK_STREAM)
    if s.connect_ex((start_ip, port)) == 0: return start_ip
    
    while time.time() - start_time <= SERVER_SEARCH_TIME:
        ip_next = next_ip(ip_next) #Search going up
        ip_previous = previous_ip(ip_previous) #Search going down
        
        s = socket(AF_INET, SOCK_STREAM)
        if s.connect_ex((ip_next, port)) == 0: return ip_next
        
        s = socket(AF_INET, SOCK_STREAM)
        if s.connect_ex((ip_previous, port)) == 0: return ip_previous

    return start_ip
def connection_handler(): #Listen for messages from the server
    global client_socket
    global lobby_message
    lobby_message = "Connecting to the server..."
    
    #Server Address
    SERVER_PORT = 14810
    server_ip = search_server(gethostbyname(gethostname()), SERVER_PORT)
    SERVER_ADDR = (server_ip, SERVER_PORT)
    
    try:
        #Try to connect
        client_socket.connect(SERVER_ADDR)
        lobby_message = "Waiting for players..."
        send_message(["enter_lobby", username])
        
        while True:
            message = pickle.loads(client_socket.recv(1024))

            #Create a thread to handle the message processing
            Thread(target = process_message,args = (message,)).start()
    except Exception as ex:
        if str(ex).__contains__("[WinError 10061]"): #Can't find the server
            global connection_failed
            
            client_socket = socket(AF_INET, SOCK_STREAM)
            
            #Notifying the player
            time.sleep(1.5)
            lobby_message = "No server was found, try again later..."
            time.sleep(1.5)
            lobby_message = "You'll be sent back to the main menu."
            time.sleep(1.5)
            
            connection_failed = True
        else: print(ex)
        return
def send_message(message):
    client_socket.send(pickle.dumps(message))
    print("Sent:", message)
    time.sleep(0.01) #Some delay for the client
def process_message(message): #Filter the message service
    service = message[0]
    data = message[1]

    print("Recieved:", message)
    
    match service:
        case "update_nplayers":
            global nplayers
            nplayers = data
        case "update_usernames":
            global usernames
            usernames = data
        case "update_message":
            global lobby_message
            lobby_message = data
        case "update_game_state":
            global playing
            playing = data
        case "board_indexes":
            create_cards_board(data) 
        case "flip_card":
            for card in board:
                if card.id == data:
                    card.flip()
        case "turn":
            global can_play
            global moves
            can_play = data
            if data: 
                moves = 2
                CHANGE_TURN.play().set_volume(VOL)
        case "leaderboard":
            global leaderboard
            leaderboard = data
        case "matched":
            if data: MATCHED.play().set_volume(VOL)
            else: NOT_MATCHED.play().set_volume(VOL)
        case "position":
            global leaderboard_highlight
            leaderboard_highlight = data
            if data == 1: WON_GAME.play().set_volume(VOL)

#Game
def check_click():
    global moves
    for card in board:
        if card.clicked():
            if moves - 1 >= 0: moves -= 1 
            send_message(["flip_card",[card.id, card.image_id]])
def create_cards_board(indexes): #Board of card objects
    #Needs to be a square root of 4, 16, 32
    side_length = round(math.sqrt(len(indexes))) 
    
    board_x, board_y = WIDTH/2, HEIGHT/2
    card_width, card_height = 150, 150
    gap = 20
    
    board_width_center = ((card_width+gap)*side_length)/2 - card_width/2
    board_height_center = ((card_height+gap)*side_length)/2 - card_height/2
    
    #Create cards
    for i in range(side_length):
        for j in range(side_length):
            index = indexes[len(board)] #Take next index
            board.append(Card((board_x + j*(card_width + gap)) - board_width_center,
                              (board_y + i*(card_height + gap)) - board_height_center,
                              card_width, card_height,
                              index))
def quit(): #End the program
    try: client_socket.recv(0)
    except: client_socket.close()
    pygame.quit()
    sys.exit()

###
# VARIABLES
###

#Create socket
client_socket = socket(AF_INET, SOCK_STREAM)

#Window configuration
WIDTH, HEIGHT = pygame.display.set_mode((0, 0), pygame.FULLSCREEN).get_size()
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("MemoryCraft")

#Assets
ARROW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
FONT_PATH = ASSETS_PATH + "fonts/minecraft.otf"

#Sound
CHANGE_TURN = pygame.mixer.Sound(ASSETS_PATH + "sound/change_turn.mp3")
WON_GAME = pygame.mixer.Sound(ASSETS_PATH + "sound/won_game.mp3")
MATCHED = pygame.mixer.Sound(ASSETS_PATH + "sound/matched.mp3")
NOT_MATCHED = pygame.mixer.Sound(ASSETS_PATH + "sound/not_matched.mp3")
pygame.mixer.music.load(ASSETS_PATH + "sound/minecraft_lullaby.mp3")
pygame.mixer.music.set_volume(VOL)
pygame.mixer.music.play(-1)

#Images
BACKGROUND_MENU = pygame.transform.scale(pygame.image.load(ASSETS_PATH + "images/background_menu.png"), (WIDTH, HEIGHT))
BACKGROUND_GAME = pygame.transform.scale(pygame.image.load(ASSETS_PATH + "images/background_game.png"), (WIDTH, HEIGHT))
MAIN_TITLE = pygame.image.load(ASSETS_PATH + "images/mainTitle.png")
ICON = pygame.image.load(ASSETS_PATH + "images/icon.png")
pygame.display.set_icon(ICON) 

#UI 
leaderboard_highlight = 0
leaderboard = []
username = ""
usernames = []
nplayers = ""
lobby_message = "Connecting to the server..."

#Game
CLOCK = pygame.time.Clock()
connection_failed = False
playing = False
can_play = False
board = []
moves = 2

###
# MAIN
###

def main_menu():
    global connection_failed
    global username
    connection_failed = False
    
    IMAGE_TITLE = Image(WIDTH/2, 150, MAIN_TITLE, 1050, 150)
    LABEL_USERNAME = Label(WIDTH/2, HEIGHT/2-35, create_font(30), "Choose A Username", color = (148,148,148), w = 400, h = 50, align = "right")
    TEXTBOX_USERNAME = TextBox(WIDTH/2, HEIGHT/2, 400, 50, create_font(25), username)
    BUTTON_LOBBY = Button(WIDTH/2, HEIGHT - 150, 450, 60, create_font(30), "Enter Lobby")
    
    while True:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.KEYDOWN: TEXTBOX_USERNAME.keydown(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    TEXTBOX_USERNAME.clicked()
                    if BUTTON_LOBBY.clicked():
                        #Save username
                        if TEXTBOX_USERNAME.text.isspace() or TEXTBOX_USERNAME.text == "": username = f"Player{random.randint(0, 999999)}"
                        else: username = TEXTBOX_USERNAME.text
                        
                        #Connection
                        Thread(target = connection_handler,args = (),daemon=True).start() #Connect to the server
                        
                        pygame.mouse.set_cursor(ARROW_CURSOR)
                        waiting_room()
        
        #Check if anything is hovered
        if not any(item.hovered() for item in [BUTTON_LOBBY, TEXTBOX_USERNAME]):
            pygame.mouse.set_cursor(ARROW_CURSOR)
        
        draw_background(BACKGROUND_MENU)
        for item in [LABEL_USERNAME, TEXTBOX_USERNAME, BUTTON_LOBBY, IMAGE_TITLE]:
            item.draw()
        
        pygame.display.update() 
        CLOCK.tick(FPS)
def waiting_room():
    LABEL_NPLAYERS = Label(WIDTH/2, 90, create_font(100), nplayers, w = WIDTH)
    LABEL_MESSAGE = Label(WIDTH/2, HEIGHT-200, create_font(75), lobby_message, w = WIDTH)
    
    while True:
        if connection_failed: main_menu()
        if playing: game()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
        
        draw_background(BACKGROUND_MENU)
        LABEL_NPLAYERS.text = nplayers
        LABEL_NPLAYERS.draw()
        LABEL_MESSAGE.text = lobby_message
        LABEL_MESSAGE.draw()
        for i in range(len(usernames)):
            Label(WIDTH/2, 300 + (i*65), create_font(60), usernames[i]).draw()
        
        pygame.display.update() 
        CLOCK.tick(FPS)
def game():
    global moves
    LABEL_USERNAME = Label(WIDTH/2, 50, create_font(40), username, text_shadow=True)
    LABEL_TURN = Label(WIDTH/2, HEIGHT - 80, create_font(50), "", text_shadow=True)
    
    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.MOUSEBUTTONDOWN and moves > 0 and can_play :
                if event.button == 1: check_click()
                        
        draw_background(BACKGROUND_GAME)
        
        for card in board: card.draw()
            
        LABEL_TURN.text = "It's Your Turn!" if can_play else ""
        LABEL_TURN.draw()
        LABEL_USERNAME.draw()
        
        pygame.display.update() 
        CLOCK.tick(FPS)
    #pygame.mixer.music.fadeout(1000)
    game_over()
def game_over():
    BUTTON_EXIT = Button(WIDTH/2, HEIGHT - 120, 450, 60, create_font(30), "Leave")
    LABEL_TITLE = Label(WIDTH/2, 100, create_font(65), "Leaderboard")
    LABEL_USERNAME = Label(WIDTH/2, 250, create_font(40), "Username")
    LABEL_SCORE = Label(WIDTH/2 + 300, 250, create_font(40), "Score")
    
    while not playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and BUTTON_EXIT.clicked(): quit()
        if not BUTTON_EXIT.hovered(): pygame.mouse.set_cursor(ARROW_CURSOR)
                
        draw_background(BACKGROUND_MENU)
        
        for item in [LABEL_TITLE, LABEL_USERNAME, LABEL_SCORE, BUTTON_EXIT]: item.draw()
        for i, player in enumerate(leaderboard):
            txt_color = (40,255,40) if int(player[0]) == leaderboard_highlight else (255,255,255)
            
            Label(WIDTH/2 - (LABEL_SCORE.x - WIDTH/2), 310 + (i*65), create_font(40), player[0], color = txt_color).draw() #position
            Label(LABEL_USERNAME.x, 310 + (i*65), create_font(40), player[1], color = txt_color).draw() #username
            Label(LABEL_SCORE.x, 310 + (i*65), create_font(40), player[2], color = txt_color).draw() #score
        
        pygame.display.update() 
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main_menu()