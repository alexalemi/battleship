import pexpect, re, sys
from scipy import zeros

from commonpaths import *
PATHTOPROGS = PLAYER_PATH


class ProgramPlayer:
    """ This class holds a player, can create a pexcept method which will allow
    interaction with the program through input and output through a pseudoterminal
    """

    def __init__(self,name,testing=False):
        """Initializer takes the name of the program, to be found in the players
        director. """
        PATHTOPROGS = PLAYER_PATH        
        if testing:
            PATHTOPROGS = WORKING_PATH
        self.name = name
        print "Opening %s" % PATHTOPROGS + self.name
        #self.child = pexpect.spawn( '/bin/bash ' + PATHTOPROGS +self.name)
        self.child = pexpect.spawn( PATHTOPROGS +self.name, logfile=sys.stderr)
        self.child.delaybeforesend= 0
	self.child.expect('>')
        
        self.flag = 0
        
        self.myboard = zeros((10,10),dtype='a')
        self.boardstring = ""
        self.shiphealth = {'C':5, 'B':4, 'D':3,'S':3, 'P':2}
        self.shipnames = ['C','B','D','S','P']
        self.shiplengths = [5,4,3,3,2]
        
        self.guessboard = zeros((10,10),dtype='a')
        self.lastguess = ''
        self.opponentsships = ['C','B','D','S','P']

        self.boardmatchstring = '([A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R])\s*>'
        self.boardmatchre = self.child.compile_pattern_list(self.boardmatchstring)

        self.guessmatchstring = '([A-J][0-9])\s*>'
        self.guessmatchre = self.child.compile_pattern_list(self.guessmatchstring)

        self.defaultstring = '>'
        self.defaultre = self.child.compile_pattern_list(self.defaultstring)

    def send(self,cmd):
        """Send a message to the program. """
        
        #print "Sending command: %s" % cmd
        
        self.child.sendline(cmd)
        
    def finishit(self):
        """ You've failed out, lets just give up and terminate """
        
        print "You've failed too many times, you're done."
        
        self.kill()
        self.poll(pexpect.EOF)
        
        self.child.terminate()
        
        raise Exception("FailWhale")
        
        
    def punish(self):
        """ Punish the program, if the flags get too high, raise the FailWhale """
        
        self.flag += 1
        
        self.send('E')
        self.defaultpoll()
        print "Program failed in some way, taking a penalty.  Current count: %d" % self.flag
        if self.flag > 3:
            raise Exception("FailWhale")
        self.finishit()
            
        #raise Exception("Error")
            
            
    def poll(self,match='>',timeout=1):
        """ Poll the program for a response, by default just look for the next 
        input.  By default just progress, and set the timeout of 1 """
        
        try: 
            self.child.expect(match,timeout=timeout)
            if match != '>' and match != pexpect.EOF:
                if self.child.match:
                    out = self.child.match.groups()[0]
                    return out
                else:
                    self.punish()             
            

        except:
            self.punish()



    def polllist(self,matchlist,timeout=1):
        """ Poll the program for a response, by default just look for the next 
        input.  By default just progress, and set the timeout of 1 """
        
        try: 
            self.child.expect_list(matchlist,timeout=timeout)
            if self.child.match:
                out = self.child.match.groups()[0]
                return out
            else:
                self.punish()             
            

        except:
            self.punish()
            


    def defaultpoll(self,timeout=1):
        """Default poll with the compiled thing, to try to save time"""
        try: 
            self.child.expect_list(self.defaultre,timeout=timeout)

        except:
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
        
        board = self.polllist(self.boardmatchre)
        
        #print "Created board: "
        #print board
        
        return board
        
    def guess(self):
        """ Passes along F, asking program to make a guess """
        self.send('F')
        guess = self.polllist(self.guessmatchre)
        
        #print "Made guess: "
        #print guess
        return guess
        
        
    def kill(self):
        """ Kill the process """
        self.send('K')
        try:
            self.poll(pexpect.EOF)
        except "TIMEOUT":
            self.punish()
        finally:
            self.child.terminate()
        
        print "Process terminated"
        
    def result(self,status):
        """ This passes the result of the last guess """
        self.send(status)
        self.defaultpoll()
        
        
    def info(self,guess):
        """ This sends along the opponent's guess. """
        self.send('O '+guess)
        self.defaultpoll()
        
        
        
    def endgame(self,status):
        """ This notifies of a win or loss. """
        self.send(status)
        self.defaultpoll()
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
                    self.punish()
                    self.genboard()
                    break
                try:
                    self.myboard[x+down*j,y+right*j] = self.shipnames[i]
                except IndexError:
                    print "Bad Board created, ran off board"
                    self.punish()
                    self.genboard()
                    break

        #print "Board created"
        #self.printboard()

    def totalhealth(self):
        """ Returns total unhit ship spots, to be used to check endgame condition"""
        return sum(self.shiphealth.values())


    def makeguess(self):
        """ Make a guess. Store guess as last guess for use with game board """
        guess = self.guess()
        self.lastguess = guess
        
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
                self.result(status)
            self.lastguess = ''
            
                

    def checkguess(self,guess):
        """ Check an opponents guess against you're game board. """
        self.info(guess)
        
        coords = self.getcoords(guess)
        val = self.myboard[coords]
        if val == '' or val == '0':
            status = 'M'
            self.myboard[coords] = 0
            return status
        elif val.isalpha():
            status = 'H'
            self.myboard[coords] = 'X'
            if val in self.shipnames:
                self.shiphealth[val] -= 1
                if self.shiphealth[val] == 0:
                    status = 'S ' + val
                    return status
            return status
                    
                
             
        
if __name__ == '__main__':
    Q = ProgramPlayer('ranman.py')
    for i in range(1000):
        print "ON TURN: %d" % i
        Q.guess()
        Q.reinit()
    
        
        
        
