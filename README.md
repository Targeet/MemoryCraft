INTRODUCTION

This game is called MemoryCraft, it's made in python and it is a LAN multiplayer game, meaning you can play it with other people if they are in the same Network.

MEMORYCRAFT RULES

The rules of the game are very simple.
- When the game starts, all the players get the same board of cards.
- On each turn, the player has 2 moves, he has to click 2 cards and try to match them.
- If he successfully manages to match the cards, he gets to play another turn.
- The game goes on until all the cards are matched and finally the game ends, revealing the leaderboard.

PYGAME

To make this game in python, i used a library called pygame, it helps with drawing things in the screen aswell as managing game loops, sound effects and collision detection.

EXE FILE

In both the client and the server there's a python file called "client/server_exe.py", this file is used to create a build that contains an executable.
It uses the library called "cx_Freeze". 

To create a build, open the cmd and type "py client_exe.py build" while in the client folder.
This command will create a build folder inside the client directory, the build contains all the libraries and assets used in the project and also the "main.exe".

SETTINGS JSON

In both directories there is a file called "settings.json" (in the client directory you can find it in the assets folder), this file contains some of the most important variables used in the game (volume, FPS, max_players etc.). 
This file is necessary because the code of an executable is not modifiable.

CREDITS

Every image and sound used in this project are not mine, i got everything online and here are some of the sources.

- Main menu title: https://textcraft.net
- Cards images: https://minecraftfaces.com
- Sound effects: application called "Zedge" -> https://www.zedge.net
