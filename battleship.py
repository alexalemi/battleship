"""
The main battleship game logic container
"""

import os
from collections import Counter
import sys
import random
import pexpect
import logging
logging.basicConfig(level=logging.INFO)

ROOT = os.path.realpath(os.path.dirname(sys.argv[0]))

class Process(object):
    """ A small wrapper to abstract the interaction with the process """
    def __init__(self,path,*args,**kwargs):
        self.shortname = os.path.basename(path)
        logging.debug("Initializing process for %s, path:%s", self.shortname, path)
        self.p = pexpect.spawn(path,*args,**kwargs)

    def sendline(self, s, *args, **kwargs):
        logging.debug("Sending %r to %s", s, self.shortname)
        self.p.sendline(s, *args, **kwargs)
        #consume what we just sent
        self.p.readline()

    def readline(self, *args, **kwargs):
        # logging.debug("Retrieving from %s", self.shortname)
        line = self.p.readline(*args, **kwargs)
        logging.debug("Retrieved %r from %s", line, self.shortname)
        return line

    def readboard(self, *args, **kwargs):
        """ Read an entire board """
        boardstrings = []
        for i in xrange(10):
            boardstrings.append( self.readline().strip() )
        
        board = {}
        for j,line in enumerate(boardstrings):
            for i,c in enumerate(line):
                if c != "0":
                    board[(i,j)] = c
        return board

class BoardError(Exception):
    def __init__(self, player):
        self.player = player

class TimeoutError(Exception):
    def __init__(self, player):
        self.player = player

class BattleshipGame(object):
    """ A single instance of a battleship game """

    def __init__(self, opp0, opp1):
        if random.random() < 0.5:
            self.opp0 = opp0
            self.opp1 = opp1
            self.switch = False
        else:
            self.opp0 = opp1
            self.opp1 = opp0
            self.switch = True
        
        # the boards for the two players
        self.board0 = {}
        self.board1 = {}

        self.winner = 0.5


    def _gameinit(self):
        """ Initialize a game and catch errors """
        try:
            self._initialize_processes()
            self._read_boards()
            self._validate_boards()
        except BoardError as e:
            self.winner = 1-e.player
            return 1
        except TimeoutError as e:
            self.winner = 1-e.player
            return 1
        return 0


    def game(self):
        """ Run a game from start to finish """
        self._gameinit()



        return self.winner if not self.switch else 1-self.winner

    def _initialize_processes(self):
        # Hold the popen objects for the two players
        self.p0 = Process(os.path.join(ROOT, self.opp0))
        self.p1 = Process(os.path.join(ROOT, self.opp1))

        #Try to tell each of them their opponents name
        self.p0.sendline("0, {}".format(self.opp1))
        self.p1.sendline("1, {}".format(self.opp0))

    def _read_boards(self):
        self.board0 = self.p0.readboard()
        self.board1 = self.p1.readboard()

    def _validate_boards(self):
        """ Check to see if the board is valid """
        validcount = Counter("AAAAABBBBSSSDDDPP")

        count0 = Counter(self.board0.values())
        if count0 != validcount:
            logging.error("ERROR on player 0 board")
            raise BoardError(0)

        count1 = Counter(self.board1.values())
        if count1 != validcount:
            logging.error("ERROR on player 1 board")
            raise BoardError(1)
        
if __name__ == "__main__":
    Q = BattleshipGame('test.py','test_bad.py')
