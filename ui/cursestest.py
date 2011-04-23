import curses
import curses.wrapper

import time

def main(stdscr):
    stdscr.refresh()
    
    begin_x = 2
    begin_y = 0
    height = 24
    width = 33
    middlewidth = 9
    shipwidth = 3
    shipheight = 6
    
    bold = curses.A_STANDOUT
    
    #Define the colorscheme
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE )
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED )
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE )
    # for miss use an X in 0
    misscolor = curses.color_pair(0)
    # for a hit use and X in 2
    hitcolor = curses.color_pair(2)
    
    #for other board, for miss use X in 0
    # for ship use 3
    shipcolor = curses.color_pair(3)
    # for ship hit use 2
    
    #make the player board
    playerBoard = curses.newwin(height,width,begin_y,begin_x)
    spacer = '-'*33
    playerBoard.addstr('Guessing board  \n')
    playerBoard.addstr('    A  B  C  D  E  F  G  H  I  J ')
    #playerBoard.addstr(spacer)
    for i in range(10):
        playerBoard.addstr(' %d ' % i)
        for j in range(10):
            playerBoard.addstr('[ ]')
        #playerBoard.addstr(spacer)
    playerBoard.refresh()
    
    #make the playership indicator
    playerShips = curses.newwin(shipheight,shipwidth,begin_y+2,begin_x+width+3)
    playerShips.addstr('[C][B][D][S][P]')
    playerShips.refresh()
    
    
    #make the opponent Board
    opponentboardstart = 2*begin_x + width + middlewidth
    opponentBoard = curses.newwin(height,width,begin_y,opponentboardstart)
    spacer = '-'*33
    opponentBoard.addstr(' Your board, opponents guesses \n')
    opponentBoard.addstr('    A  B  C  D  E  F  G  H  I  J ')
    #playerBoard.addstr(spacer)
    for i in range(10):
        opponentBoard.addstr(' %d ' % i)
        for j in range(10):
            opponentBoard.addstr('[ ]')
        #playerBoard.addstr(spacer)
    opponentBoard.refresh()
    
    
    #make the opponent ship indicator
    opponentShips = curses.newwin(shipheight,shipwidth,begin_y+2,opponentboardstart + width+3)
    opponentShips.addstr('[C][B][D][S][P]')
    opponentShips.refresh()
    
    
    #output at bottom
    outputScreen = curses.newwin(5,90,15,0)
    outputScreen.addstr('-'*90)
    for i in range(10):
        outputScreen.insstr('fasdfadf asdfasdf asdf asdf asdf \n ')
        outputScreen.insstr('  %d  ' % (i) )
        outputScreen.refresh()
    outputScreen.refresh()
    
    

    
    time.sleep(10)
    
    

curses.wrapper(main)   





