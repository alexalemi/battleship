"""
The main battleship game logic container
"""

# FIX FOR PYPY
# import sys
# sys.path.append("/home/alemi/anaconda/lib/python2.7/site-packages/")

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
    def __init__(self, path, *args,**kwargs):
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

    def readguess(self, *args, **kwargs):
        """ Read a guess from the player, report as tuple """
        line = self.p.readline(*args, **kwargs)
        logging.debug("Got raw guess line %s", line)
        guess = tuple(map(int, line.strip().split(",")))
        logging.info("%s guessed %r", self.shortname, guess)
        return guess

    def sendguess(self, guess):
        self.sendline("{},{}".format(*guess))

    def readboard(self, *args, **kwargs):
        """ Read an entire board """
        logging.debug("Attempting to read a board from %s", self.shortname)
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


class BattleshipPlayer(object):
    """ A small container for the data
    associated with a player """
    def __init__(self, process, opponent, playernum):
        self.name = process
        self.opponent = opponent
        self.playernum = playernum
        self.p = None
        self.board = {}
        self.guesses = set()
        self.lives = {"A" : 5, "B": 4, "D": 3, "S": 3, "P": 2}

        self.initialize_process()

    def initialize_process(self):
        # Hold the popen objects for the two players
        self.p = Process(os.path.join(ROOT, self.name))
        self.p.delaybeforesend = 0
        #Try to tell each of them their opponents name
        self.p.sendline("{}, {}".format(self.playernum, self.opponent))

    def read_board(self):
        self.board = self.p.readboard()

    @property
    def alive(self):
        """ Check to see if the player is still alive """
        if any(self.lives.values()):
            return True
        return False


class BattleshipGame(object):
    """ A single instance of a battleship game """

    def __init__(self, opp0, opp1):

        if random.random() < 0.5:
            self.switch = False
        else:
            opp0, opp1 = opp1, opp0
            self.switch = True
        self.p0 = BattleshipPlayer(opp0, opp1, 0)
        self.p1 = BattleshipPlayer(opp1, opp0, 1)

        self.turns = 0

        self.guesser = self.p0
        self.marker = self.p1

        self.finished = False
        self.winner = 0.5

    def _gameinit(self):
        """ Initialize a game and catch errors """
        try:
            self.p0.initialize_process()
            self.p1.initialize_process()
            self.p0.read_board()
            self.p1.read_board()
            self._validate_boards()
        except BoardError as e:
            self.winner = 1-e.player
            return 1
        except TimeoutError as e:
            self.winner = 1-e.player
            return 1
        return 0

    def turn(self):
        # main game loop
        self.turns += 1
        logging.debug("Entering turn %d", self.turns)

        # need to read a guess from the guesser
        guess = self.guesser.p.readguess()
        # send the guess to the marker
        self.marker.p.sendguess(guess)

        # check to see if this is a hit
        ship = self.marker.board.get(guess, '')
        if ship:
            # we have a hit, if this hasn't been
            # guessed before, reduce the lives of the ship
            # by one
            if guess not in self.guesser.guesses:
                self.guesser.guesses.add(guess)
                self.marker.lives[ship] -= 1
                # check to see if we've killed the ship
                if self.marker.lives[ship] == 0:
                    # we've killed the ship, check to see if we've won
                    if not self.marker.alive:
                        # Just won.
                        logging.info("Won the game!")
                        self.guesser.p.sendline("W")
                        self.winner = 1 - self.turns % 2
                        self.finished = True
                        return
                    else:
                        # sunk a ship, but not dead yet
                        logging.info("Sunk the %r ship", ship)
                        self.guesser.p.sendline("S{}".format(ship))
                else:
                    # just got a hit
                    logging.info("Registered a hit")
                    self.guesser.p.sendline("H")
            else:
                # a hit, but already counted
                logging.info("Registered a REPEATED hit")
                self.guesser.p.sendline("H")
        else:
            # we had a miss, send a miss
            logging.info("Miss")
            self.guesser.p.sendline("M")
       
        # swap players
        self.guesser, self.marker = self.marker, self.guesser

    def game(self):
        """ Run a game from start to finish """
        logging.info("Running a full game.")
        self._gameinit()

        while not self.finished:
            self.turn()

        return self.winner if not self.switch else 1-self.winner


    def _validate_boards(self):
        """ Check to see if the board is valid
        raise an error if there is a problem with the board"""
        validcount = Counter("AAAAABBBBSSSDDDPP")

        count0 = Counter(self.p0.board.values())
        if count0 != validcount:
            logging.error("ERROR on player 0 board")
            raise BoardError(0)

        count1 = Counter(self.p1.board.values())
        if count1 != validcount:
            logging.error("ERROR on player 1 board")
            raise BoardError(1)
        
if __name__ == "__main__":
    Q = BattleshipGame('test.py','test2.py')
    print Q.game()
