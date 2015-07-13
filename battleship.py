"""
Run a game of battleship between two processes.

to run, give the names of the two binaries to execute.
 e.g. python game.py /path/to/engine1 /path/to/engine2

The engine expects the processes to communicate over a socket.
When the engine runs your process, it will send a single 
command line argument, which is the port on which you should connect
to.

At that point, the engine will randomly determine who goes first,
and send each engine a message on stdin,

  0, opponent_name\n

where the first character tells whether you go first or second,
and the second string is your opponents name.

Each binary must then report an ascii representation of a 10x10 game board
with: 
    A for the aircraft carrier (length 5),
    B for a battle ship (length 4)
    S for a submarine (length 3)
    D for a destroyer (length 3)
    P for a patrol boat (length 2)
    0 for an empty square

for example, an example board would be:

    0000000000\n
    00000000PP\n
    00B0000000\n
    00B000A000\n
    00B000ASSS\n
    00BDDDA000\n
    000000A000\n
    000000A000\n
    0000000000\n
    0000000000\n

At that point, if it is your turn, you must report your guess
as a comma separated tuple, 0-indexed, e.g.

    0, 5\n

The engine will report back on stdin, either 'H\n' if a hit,
'M\n' if a miss, 'SX\n' if you sunk a ship, where X is one of the 
boat characters above, and 'W\n' if you won the game.

If it is not your turn, the engine will notify you of 
your opponents guess in the form a comma separated tuple

  0, 5\n

"""


import os
import socket
from collections import Counter
import sys
import random
import subprocess
import futures
import time
from random import randrange
import logging
logging.basicConfig(level=logging.DEBUG)

ROOT = os.path.realpath(os.path.dirname(__file__))
WORKERS = 10

class Process(object):
    """ A small wrapper to abstract the interaction with the process """
    def __init__(self, path, port=None, *args,**kwargs):
        self.shortname = os.path.basename(path)
        logging.debug("Initializing process for %s, path:%s", self.shortname, path)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        done = False
        while not done:
            try:
                self.port = randrange(5000,10000)
                server_address = ('localhost', self.port)
                self.sock.bind(server_address)
                break
            except socket.error:
                logging.warning("We hit a bad port (%d) bind, try again", self.port)
                # we presumabely failed to bind, try again, but sleep a bit
                time.sleep(0.01)
                continue

        logging.debug("Creating socket: %r", server_address)
        self.p = subprocess.Popen([path, str(self.port)], *args, **kwargs) #, stdin=subprocess.PIPE,
                    #stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs)

        self.sock.listen(1)
        logging.debug("Waiting for connection...")
        self.connection, self.client_address = self.sock.accept()
        self.connection_file = self.connection.makefile("r+")

    def __del__(self):
        # clean up the process and port
        self.p.terminate()
        self.connection_file.close()
        self.connection.close()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.close()

    def sendline(self, s, *args, **kwargs):
        """ Send a line by writing a line to the connection_file buffer """
        logging.debug("Sending %r to %s", s, self.shortname)
        self.connection_file.write(s + '\n')
        self.connection_file.flush()

    def readline(self, bts=16,*args, **kwargs):
        """ Read a line from the connection file_handler object """
        msg = self.connection_file.readline()
        logging.debug("Retrieved %r from %s", msg, self.shortname)
        return msg

    def readguess(self, *args, **kwargs):
        """ Read a guess from the player, report as tuple """
        line = self.readline(*args, **kwargs)
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
            boardstrings.append( self.readline(1).strip() )
        
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

    def __del__(self):
        del self.p

    def initialize_process(self):
        # Hold the popen objects for the two players
        prog = os.path.join(ROOT, self.name)
        logging.debug("Launching process %s", prog)
        self.p = Process(prog)
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

    def __del__(self):
        del self.p0
        del self.p1

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
            self.finished = True
            return 1
        except TimeoutError as e:
            self.winner = 1-e.player
            self.finished = True
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

def game(opp0, opp1):
    engine = BattleshipGame(opp0, opp1)
    return engine.game()

def unpackgame(opps):
    return game(*opps)

def match(opp0, opp1, N=1000):
    """ Run a match between opp1 and opp2, which consists of N games """
    with futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
        return [res for res in executor.map(unpackgame, ((opp0,opp1) for i in xrange(N)))]

opp1 = "players/randguess.py"
opp2 = "players/tile.py"
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
    else:
        print game(sys.argv[1], sys.argv[2])
