# RPG Level Calculator in Python
Video Demo: https://www.youtube.com/watch?v=edv3HaV37SA  
Name: Luis Valter Machado Junior  
Edx: AxeWalter  
GitHub: AxeWalter

## Motivation

This Python calculator has designed to solve a problem my players were 
facing during our RPG sessions. At the end of every session the players are
awarded a number of experience points (XP) depending on their actions 
during the session, including things like completing quests, exploring 
new places, sailing to new islands, defeating enemies and so on. We play 
a variation of the classical D&D system for tabletop RPG`s, so our level 
up system is a little different. The players level up quicker, which can 
be a problem when tracking the levels is all done by the players themselves.
We always play on Fridays nights, and the can sessions last up to 5 hours.
At the end of it, when the RPG master distributes the XP points, players 
are a little tired and level calculations tended to go wrong. To solve 
this, I designed this simple Python calculator executable to automate the 
process. This way, the players only need to keep track of their total XP 
for the campaign (this being their whole XP points for all the episodes), 
add the amount of XP points given in the episode and input in the 
calculator, which will output their level and spare XP points for their 
current level (this way they have an idea of how far they are to leveling 
up again).

## Design

To build the calculator I used Python. The “backend” logic is quite simple:
we ran a loop that gets what the player inputs as their total XP and 
compares to a variable called `lvl` that starts at zero (and this is not 
a mistake, just like Python starts to count at zero, in our RPG the players
start at level zero). The level up system goes like this: to level up from
0 to 1 you need 100XP, from 1 to 2 200XP, and so on. In other words, the
formula to level up is (Current Level + 1) * 100 . In the code have the
`x` variable, which is the input of the player XP, and the `lvl`, which
works not only as the indicator of the level of the players, but, most
importantly, as our counter for the while loop. We compare those two
variables in a way that `WHILE` `x` is higher or equals to `(lvl +1) * 100`,
we’re going to subtract `(lvl +1) * 100` from `x`, add +1 to `lvl` and
restart the loop. In other words, if there's enough XP points, `x`, to
level up, we add +1 to the player level, `lvl`, subtract the level up
amount of XP from the player total XP, and compare again. This goes until
the amount of XP, `x`, is not enough to level up again. When this happens,
the loop ends and the GUI displays the player current level, `lvl`, and
their remaining XP, `x`.

## Libraries, GUI and Executable

The GUI was built with Tkinter, a common Python library for this purpose. 
At last, as I explained in the video, turning this code into an executable 
was very important, because most of the players don't code and, chances are, 
handling them a script to run in a terminal would not solve much of the math
problems. Because of this, I used the PyInstaller library to turn the Python
script into an executable file. After coding the script, just had to install
the library and, at the terminal, 
run `pyinstaller --onefile –noconsole name_of_script.py` to create the 
executable. For this first version I wanted to make the simplest program 
possible, meaning I did not want any dependencies with the executable. 
This is the reason I didn`t attach a database, for example, to keep the 
players XP points in the program. But, for the future I intend to expand 
the project, attaching not only a SQL database for keeping the players XP 
points, but also items and so on.
