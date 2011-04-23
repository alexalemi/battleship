from battleship.scripts.programplayer import ProgramPlayer

from humanplayer import HumanPlayer

import random
import time
from datetime import datetime

#from commonpaths import *

#from battle.models import Game, Player, Program

class Game:
    """ This is the game class, it keeps track of a single game between two players """

    def __init__(self,player2name,testing=False):
        """ Initialize with both players """
        self.player1name = 'human'
        self.player2name = player2name

        
        self.player1 = HumanPlayer(self.player1name,testing)
        self.player2 = ProgramPlayer(self.player2name,testing)
        
        self.playernames = [self.player1name,self.player2name]
        self.players = [self.player1, self.player2]
        
        self.finished = False
        self.firstplayer = 0
        self.turn = 0
        self.winner = -1
        self.winnername = ""
        self.remaininghealth = 0
        self.FailWhale = 0
        self.time = 0

        self.moves = ""
        self.player1board = ""
        self.player2board = ""
        
        self.info = {}
        
    def reinit(self):  
        """ change the variables back to their initial ones """   
        print "REINITIALIZING..."   
        self.finished = False
        self.firstplayer = 0
        self.turn = 0
        self.winner = -1
        self.winnername = ""
        self.remaininghealth = 0
        self.FailWhale = 0
        self.time = 0
        self.info = {}

        self.moves = ""

        time.sleep(0.1)

    def makeboards(self):
        """ Tells both players to generate their boards """
        A = self.firstplayer
        B = 1*(not A)
        try:
            self.players[A].genboard(self.playernames[B])
        except Exception("FailWhale"):
            print "FAILWHALE on board generation for player A"
            self.FailWhale = 1
            self.announcewinner(B)
            return

        
        try:
            self.players[B].genboard(self.playernames[A])
        except Exception:
            print "FAILWHALE ON board generation for player B"
            self.FailWhale = 1
            self.announcewinner(A)
            return 


        print "MADE BOARDS"
        
    def takeaturn(self):
        """ Take a turn, player A guesses, player B checks, player A is notified,
        make sure B didn't just lose """
        
        
        A = (self.turn + self.firstplayer)%2
        B = 1*(not A)
        
        try:
            try:
                guess = self.players[A].makeguess()
                self.moves += "F " + guess + "|"
            except Exception:
                self.FailWhale =1
                print "FAIL WHALE"
                self.announcewinner(B)
                return 1
            try:
                status = self.players[B].checkguess(guess)
                self.moves += status + "|"
            except Exception:
                self.FailWhale =1
                print "FAIL WHALE"
                self.announcewinner(A)
                return 1
            try:
                self.players[A].recordguess(status)
            except Exception:
                self.FailWhale = 1
                print "FAIL WHALE"
                self.announcewinner(B)
                return 1
            
            if status[0] == 'S':
                if self.players[B].totalhealth() <= 0:
                    self.winner = A                
                    return 1

        except UnboundLocalError:
            return 1
            

        
        self.turn += 1
        
        #print "Turn #%d" % self.turn
        #print "%s \t guessed \t %s" % (self.playernames[A], guess)
        #print "%s \t responded \t %s" % (self.playernames[B], status)
        #print 
        
        return 0

    def writedatabase(self,winner):
        """This is where I update the sqlite database with the game information"""
        #from battle.models import Game, Player, Program
        
        from datetime import datetime
                            
        if self.FailWhale == False:
            self.info['player1name'] = self.playernames[self.firstplayer]
            self.info['player2name'] = self.playernames[1*(self.firstplayer==0)]
            self.info['finished'] = True
            self.info['moves']= self.moves
            self.info['winnername'] = self.playernames[winner]
            self.info['losername'] = self.playernames[1*(winner==0)]
            self.info['duration'] = self.time
            self.info['turns'] = self.turn
            self.info['remaininghealth'] = self.remaininghealth
            self.info['player1board'] = self.player1.boardstring
            self.info['player2board'] = self.player2.boardstring
            self.info['failwhale'] = False
            
            
        else:
            self.info['player1name'] = self.playernames[self.firstplayer]
            self.info['player2name'] = self.playernames[1*(self.firstplayer==0)]
            self.info['finished'] = False
            self.info['moves']= self.moves
            self.info['winnername'] = self.playernames[winner]
            self.info['losername'] = self.playernames[1*(winner==0)]
            self.info['duration'] = self.time
            self.info['turns'] = self.turn
            self.info['remaininghealth'] = self.remaininghealth
            self.info['player1board'] = self.player1.boardstring
            self.info['player2board'] = self.player2.boardstring
            self.info['failwhale'] = True
            
        #print "OUTPUT @@%s@@" % (pickle.dumps(info))
        
        print "MADE THE INFO NAMEDTUPLE"
        


    def playgame(self,reverse=False):
        if self.FailWhale:
            return    

        if reverse:
            self.firstplayer = 1
        else:
            self.firstplayer = 0
        print "Game started between %s and %s" % (self.playernames[self.firstplayer],self.playernames[1*(self.firstplayer==0)])
        starttime = time.time()
        self.makeboards()
    
        finished = False
        while not finished:
            finished = self.takeaturn()
            

        finishtime = time.time()

        self.time = finishtime - starttime

        if not self.FailWhale:
            self.announcewinner(self.winner)

            record = [0,0]
            record[self.winner] = 1
            gameinfo = self.info

            print "Game took %f sec" % (finishtime-starttime)
            self.reinit()
        else:
            print "FAILWHALE"
            record = [0,0]
            record[self.winner] =1

            gameinfo = self.info

            self.reinit()
               
            

        
        return record, gameinfo
            
            
        
    def announcewinner(self,winner):
        """ Tell Player A they won, and B they lost """
        
        self.finished = True
        self.winner = winner
        self.winnername = self.playernames[winner]
        self.remaininghealth = self.players[winner].totalhealth()

        print "Game over: %s won!" % self.playernames[winner]
        
        try:
            self.players[winner].endgame('W')
            self.players[1*(not winner)].endgame('L')
        except Exception:
            pass
   
        self.writedatabase(winner)
        
    def terminate(self):
        for p in self.players:
            p.kill()
    

    def playgames(self,N=10):
        """This program will play N games between the two programs, half with each as first player """
                
        eachside = N/2
        
        gamedicts = []

        print "Launching playoffs"
        print 
        record =  [0 , 0]

        starttime = time.time()
        for i in range(eachside):
            newrecord, gameinfo = self.playgame()
            record[0] += newrecord[0]
            record[1] += newrecord[1]
            gamedicts.append(gameinfo)
        for i in range(eachside):
            print "REVERSED GAME"
            newrecord, gameinfo = self.playgame(reverse=True)
            record[0] += newrecord[0]
            record[1] += newrecord[1]
            gamedicts.append(gameinfo)
        
        finishtime = time.time()
        print "Playoff finished. Took %f seconds" % (finishtime- starttime)
        self.terminate()
        
        
        return record, gamedicts

def launchgame(player2):
    Q = Game(player2)
    record, gamedicts = Q.playgame()
    Q.terminate()
  
def launchgames(player1,player2, N=10,testing=False):
    
    Q = Game(player1,player2,testing)
    record, gamedicts = Q.playgames(N)
    
    #print "OUTPUT @@%s@@" % str(gamedicts)
    
    return record, gamedicts

        
if __name__ == "__main__":
    launchgame('ranman')


