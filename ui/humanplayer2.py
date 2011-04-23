import pexpect, re, sys
from scipy import zeros



"""
These are the pieces that I need.

p.genboard()
p.makeaguess()
p.checkguess()
p.recordguess()
p.totalhealth()

p.boardstring


"""



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
        self.opponentsships = ['C','B','D','S','P']

        #matching expressions
        self.boardmatchstring = '([A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R] [A-J][0-9][D|R])'

        self.guessmatchstring = '([A-J][0-9])'

        self.defaultstring = '>'

    def send(self,cmd):
        """Send a message to the program. """
        
        #print "Sending command: %s" % cmd
        
        print "Recieving command|%s" % cmd
        

        
    def punish(self):
        """ If we get here, the human made a mistake """
        print "You've made a mistake somehow. FAILWHALE! Try again or 'Q' to quit."
        #raise Exception("FailWhale")


    def poll(self,match='>'):
        """ Poll the program for a response, by default just look for the next 
        input.  By default just progress, and set the timeout of 1 """
        
        done = False
        while not done:
            expect = raw_input('>')
            expect = expect.upper()
            if expect == 'Q':
                quit()
                return
                
            
            matched = re.findall(match,expect)

            if match != '>':
                if matched:
                    out = matched[0]
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
        
        
    def kill(self):
        """ Kill the process """
        self.send('K')
        print "Closing program..."
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
                    self.genboard()
                    break
                try:
                    self.myboard[x+down*j,y+right*j] = self.shipnames[i]
                except IndexError:
                    print "Bad Board created, ran off board"
                    print self.myboard
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
    Q = HumanPlayer()
    for i in range(1000):
        print "ON TURN: %d" % i
        Q.guess()
        Q.reinit()
    
        
        
        
