import pexpect, re, sys
from scipy import zeros

import curses
import curses.wrapper

"""
These are the pieces that I need.

p.genboard()
p.makeaguess()
p.checkguess()
p.recordguess()
p.totalhealth()

p.boardstring


"""


class CursesBoard:
    """ This will hold the curses interface """
    
    def __init__(self):
    
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.stdscr.keypad(1)
        
        self.stdscr.refresh()
        
        begin_x = 2
        begin_y = 0
        height = 15
        width = 33
        middlewidth = 9
        shipwidth = 3
        shipheight = 6
        
        self.bold = curses.A_BOLD
        
        #Define the colorscheme
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE )
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED )
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE )
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA )
        # for miss use an X in 0
        self.misscolor = curses.color_pair(0)
        # for a hit use and X in 2
        self.hitcolor = curses.color_pair(2)
        self.newhitcolor = curses.color_pair(4)
        
        #for other board, for miss use X in 0
        # for ship use 3
        self.shipcolor = curses.color_pair(3)
        # for ship hit use 2
        
        #make the player board
        self.playerBoard = curses.newwin(height,width,begin_y,begin_x)
        self.spacer = '-'*33
        self.playerBoard.addstr('Guessing board  \n')
        self.playerBoard.addstr('    A  B  C  D  E  F  G  H  I  J ')
        #playerBoard.addstr(spacer)
        for i in range(10):
            self.playerBoard.addstr(' %d ' % i)
            for j in range(10):
                self.playerBoard.addstr('[ ]')
            #playerBoard.addstr(spacer)
        self.playerBoard.refresh()
        
        #make the playership indicator
        self.playerShips = curses.newwin(shipheight,shipwidth,begin_y+2,begin_x+width+3)
        self.playerShips.addstr('[C][B][D][S][P]')
        self.playerShips.refresh()
        
        
        #make the opponent Board
        opponentboardstart = 2*begin_x + width + middlewidth
        self.opponentBoard = curses.newwin(height,width,begin_y,opponentboardstart)
        self.opponentBoard.addstr(' Your board, opponents guesses \n')
        self.opponentBoard.addstr('    A  B  C  D  E  F  G  H  I  J ')
        #playerBoard.addstr(spacer)
        for i in range(10):
            self.opponentBoard.addstr(' %d ' % i)
            for j in range(10):
                self.opponentBoard.addstr('[ ]')
            #playerBoard.addstr(spacer)
        self.opponentBoard.refresh()
        
        
        #make the opponent ship indicator
        self.opponentShips = curses.newwin(shipheight,shipwidth,begin_y+2,opponentboardstart + width+3)
        self.opponentShips.addstr('[C][B][D][S][P]')
        self.opponentShips.refresh()
        
        
        #output at bottom
        self.outputScreen = curses.newwin(7,90,15,0)
        self.outputScreen.addstr('-'*90)
        self.outputScreen.refresh()
        
        self.lastrow = 0

    def drawPlayerBoard(self,board,last=None):
        #draw the player board
        self.spacer = '-'*33
        self.playerBoard.addstr(0,0,'Guessing board  \n')
        self.playerBoard.addstr('    A  B  C  D  E  F  G  H  I  J ')
        #playerBoard.addstr(spacer)
        for i in range(10):
            self.playerBoard.addstr(' %d ' % i)
            for j in range(10):
                val = board[i][j]
                if (i,j) == last:
                    if val == '0':
                        self.playerBoard.addstr('[0]',self.bold)
                    elif val == 'X':
                        self.playerBoard.addstr('[X]',self.bold + self.hitcolor) 
                    else:
                        self.playerBoard.addstr('[ ]',self.bold)
                else:
                
                    if val == '0':
                        self.playerBoard.addstr('[0]')
                    elif val == 'X':
                        self.playerBoard.addstr('[X]',self.hitcolor) 
                    else:
                        self.playerBoard.addstr('[ ]')
            #playerBoard.addstr(spacer)
        self.playerBoard.refresh()
        
        
    def drawOpponentBoard(self,board,last=None):
        #Draw the opponent Board
        
        self.opponentBoard.addstr(0,0,' Your board, opponents guesses \n')
        self.opponentBoard.addstr('    A  B  C  D  E  F  G  H  I  J ')
        #playerBoard.addstr(spacer)
        for i in range(10):
            self.opponentBoard.addstr(' %d ' % i)
            for j in range(10):
                val = board[i][j]
                if (i,j) == last:
                    if val == '':
                        self.opponentBoard.addstr('[ ]',self.bold)
                    elif val == '0':
                        self.opponentBoard.addstr('[0]',self.bold)
                    elif val == 'X':
                        self.opponentBoard.addstr('[X]',self.bold + self.hitcolor)
                    else:
                        self.opponentBoard.addstr('[%s]' % (val), self.shipcolor )
                else:
                    if val == '':
                        self.opponentBoard.addstr('[ ]')
                    elif val == '0':
                        self.opponentBoard.addstr('[0]')
                    elif val == 'X':
                        self.opponentBoard.addstr('[X]',self.hitcolor)
                    else:
                        self.opponentBoard.addstr('[%s]' % (val), self.shipcolor )
            #playerBoard.addstr(spacer)
        self.opponentBoard.refresh()
        
    def updatePlayerShips(self,ships):
    
        shipstocheck = 'CBDSP'
        
        self.playerShips.addstr(0,0,'')
        for ship in shipstocheck:
            if ship in ships:
                self.playerShips.addstr('[%c]' % ship)
            else:
                self.playerShips.addstr('[%c]' % ship, self.hitcolor )
        self.playerShips.refresh()
        
    def updateOpponentShips(self,ships):
        shipstocheck = 'CBDSP'
        
        self.opponentShips.addstr(0,0,'')
        for ship in shipstocheck:
            if ship in ships:
                self.opponentShips.addstr('[%c]' % ship)
            else:
                self.opponentShips.addstr('[%c]' % ship, self.hitcolor )
        self.opponentShips.refresh()
        
    def printToBottom(self,string,row=0):
        row = self.lastrow
        self.lastrow = ( self.lastrow + 1 )% 5
        self.outputScreen.insstr(row,0,string)
        self.outputScreen.refresh()
        
    def kill(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()



#This is going to be the HumanPlayer

class HumanPlayer:
    """ This class holds a player, can create a pexcept method which will allow
    interaction with the program through input and output through a pseudoterminal
    """

    def __init__(self,name='human',testing=False):
        """Initializer takes the name of the program, to be found in the players
        director. """

        self.name = 'human'

    
        self.flag = 0
        
        self.myboard = zeros((10,10),dtype='a')
        self.boardstring = ""
        self.shiphealth = {'C':5, 'B':4, 'D':3,'S':3, 'P':2}
        self.shipnames = ['C','B','D','S','P']
        self.shiplengths = [5,4,3,3,2]
        
        self.guessboard = zeros((10,10),dtype='a')
        self.lastguess = ''
        self.lastguessspot = None
        self.lastoppguess = None
        self.opponentsships = ['C','B','D','S','P']

        #matching expressions
        self.boardmatchstring = '([A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R])'

        self.guessmatchstring = '([A-J][0-9])'

        self.defaultstring = '>'
        
        self.curses = CursesBoard()

        

    def send(self,cmd):
        """Send a message to the program. """
        
        #print "Sending command: %s" % cmd
        
        self.curses.printToBottom("Recieving command|%s \n" % cmd)
        

        
    def punish(self):
        """ If we get here, the human made a mistake """
        self.curses.printToBottom( "You've made a mistake somehow. FAILWHALE! Try again or 'Q' to quit. \n" )
        #raise Exception("FailWhale")


    def poll(self,match='>'):
        """ Poll the program for a response, by default just look for the next 
        input.  By default just progress, and set the timeout of 1 """
        
        done = False
        while not done:
            curses.echo()
            expect = self.curses.outputScreen.getstr(5,0,20)
            #print "got <%s>" % expect
            #expect = raw_input('>')
            expect = expect.upper()
            if expect == 'Q':
                #Allow user to quit with Q
                self.curseskill()
                quit()
                return
                
            
            matched = re.findall(match,expect)

            if match != '>':
                if matched:
                    out = matched[0]
                    self.curses.outputScreen.addstr(0,0,out)
                    self.curses.outputScreen.refresh()
                    done = True
                    return out
                else:
                    self.punish() 

                    

    def reinit(self):
        """ Reinitialize game state """
        self.flag = 0
        
        self.myboard = zeros((10,10),dtype='a')
        self.shiphealth = {'C':5, 'B':4, 'D':3,'S':3, 'P':2}
        
        self.guessboard = zeros((10,10),dtype='a')
        self.lastguess = ''
        self.opponentsships = ['C','B','D','S','P']



    def newboard(self,opponentname = 'blank'):
        """ Asks the program to generate a new board"""
        self.send('N ' + opponentname)
        
        
        board = self.poll(self.boardmatchstring)
        
        #print "Created board: "
        #print board
        
        return board
        
    def guess(self):
        """ Passes along F, asking program to make a guess """
        self.send('F')
        guess = self.poll(self.guessmatchstring)
        
        #print "Made guess: "
        #print guess
        return guess

    def curseskill(self):
        self.curses.kill()

        
    def kill(self):
        """ Kill the process """
        self.send('K')
        print "Closing program..."
        self.curseskill()
        quit()
        
    def result(self,status):
        """ This passes the result of the last guess """
        self.send(status)
        #self.poll(self.defaultstring)
        
        
    def info(self,guess):
        """ This sends along the opponent's guess. """
        self.send('O '+guess)
        #self.defaultpoll()
        
        
        
    def endgame(self,status):
        """ This notifies of a win or loss. """
        self.send(status)
        #self.defaultpoll()
        self.reinit()
        
    def getcoords(self,coord):
        y = ord(coord[0]) - ord('A')
        x = int(coord[1])
        return (x,y)
        
        
    def printboard(self,guess=False):
        """ prints out board to terminal """
        board = self.myboard
        if guess:
            board = self.guessboard
        
        print "My board"
        print "-"*23
        for i in range(10):
            print "|",
            for j in range(10):
                val = board[i,j]
                if val:
                    print str(board[i,j]),
                else:
                    print " ",
            print "|"
        print "-"*23
        
    def genboard(self,opponentname='blank'):
        """Generates the internal representation of your board """
        myboard = self.newboard(opponentname)
        self.boardstring = myboard
        
        ships = myboard.split(' ')
        for i,s in enumerate(ships):
            x,y = self.getcoords(s[0:2])
            d = s[-1]
            down,right = 0,0
            if d == 'D':
                down = 1
            elif d == 'R':
                right = 1
            for j in range(self.shiplengths[i]):
                #print "inserting at %d,%d" % (x + down*j , y + right*j )
                if self.myboard[x+ down*j,y + right*j] != '':
                    print "Bad Board created, place taken"
                    print self.myboard
                    self.punish()
                    #self.genboard()
                    break
                try:
                    self.myboard[x+down*j,y+right*j] = self.shipnames[i]
                except IndexError:
                    print "Bad Board created, ran off board"
                    print self.myboard
                    self.punish()
                    #self.genboard()
                    break
        
        self.curses.drawOpponentBoard(self.myboard)
        #print "Board created"
        #self.printboard()

    def totalhealth(self):
        """ Returns total unhit ship spots, to be used to check endgame condition"""
        return sum(self.shiphealth.values())


    def makeguess(self):
        """ Make a guess. Store guess as last guess for use with game board """
        guess = self.guess()
        self.lastguess = guess
        self.lastguessspot = self.getcoords(guess)
        
        return guess

    def recordguess(self,status):
        """ Record the status of the previous guess """
        if self.lastguess:
            coord = self.getcoords(self.lastguess)
            
            if status[0] == 'M':
                self.guessboard[coord] = '0'
                self.result(status)
            elif status[0] == 'H':
                self.guessboard[coord] = 'X'
                self.result(status)
            elif status[0] == 'S':
                self.guessboard[coord] = 'X'
                self.opponentsships.remove(status[-1])
                self.curses.updatePlayerShips(self.opponentsships)
                self.result(status)
            self.lastguess = ''
            
            self.curses.drawPlayerBoard(self.guessboard,coord)
            
                

    def checkguess(self,guess):
        """ Check an opponents guess against you're game board. """
        self.info(guess)
        
        coords = self.getcoords(guess)
        self.lastoppguess = coords
        val = self.myboard[coords]
        if val == '' or val == '0':
            status = 'M'
            self.myboard[coords] = 0
            
            self.curses.drawOpponentBoard(self.myboard,coords)
            
            return status
        elif val.isalpha():
            status = 'H'
            self.myboard[coords] = 'X'
            
            self.curses.drawOpponentBoard(self.myboard,coords)
            
            if val in self.shipnames:
                self.shiphealth[val] -= 1
                if self.shiphealth[val] == 0:
                    status = 'S ' + val
                    
                    ships = [key for key,val in self.shiphealth.iteritems() if val > 0]
                    self.curses.updateOpponentShips(ships)
                    
                    return status
            return status
                    
                
             
        
if __name__ == '__main__':
    Q = HumanPlayer()
    Q.genboard('blah')
    for i in range(1000):
        #print "ON TURN: %d" % i
        guess = Q.guess()
        Q.checkguess(guess)
        Q.recordguess(guess)
        
    
        
        
        
