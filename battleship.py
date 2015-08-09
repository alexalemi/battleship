#!/usr/bin/env python2
"""
Author: Alex Alemi

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
import argparse
import json
import glob
import socket
from collections import Counter
import sys
import random
import subprocess
import concurrent.futures
import itertools
import time
from random import randrange
import functools
import signal
import logging
# logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('battleship')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('logs/battleship.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# logging.basicConfig(filename='logs/battleship.log',level=logging.DEBUG)

ROOT = os.path.realpath(os.path.dirname(__file__))
WORKERS = 2
DEFAULTN = 25
SAVERECORD=False
BUFFER = 2056
PLAYERPATH = 'players'
RECORDPATH = 'records'
TIMEOUT = 2

SHIP_LENGTHS = {"A":5, "B":4, "D":3, "S":3, "P":2}

class TimeoutError(Exception):
    def __init__(self, signum=None, frame=None):
        self.signum = signum
        self.frame = frame
    def __str__(self):
        return "there was a timeout error"

def signal_handler(signum=None, frame=None):
    raise TimeoutError(signum, frame)

def timelimit(func):
    """ A timelimit decorator """
    @functools.wraps(func)
    def timed_func(*args, **kwargs):
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(TIMEOUT)
        try:
            return func(*args, **kwargs)
        finally:
            signal.alarm(0)
    return timed_func


class Process(object):
    """ A small wrapper to abstract the interaction with the process """
    def __init__(self, path, port=None, *args,**kwargs):
        self.shortname = os.path.basename(path)
        logger.debug("Initializing process for %s, path:%s", self.shortname, path)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        done = False
        while not done:
            try:
                self.port = randrange(5000,10000)
                server_address = ('localhost', self.port)
                self.sock.bind(server_address)
                break
            except socket.error:
                logger.warning("We hit a bad port (%d) bind, try again", self.port)
                # we presumabely failed to bind, try again, but sleep a bit
                time.sleep(0.01)
                continue

        logger.debug("Creating socket: %r", server_address)
        self.p = subprocess.Popen([path, str(self.port)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs) #, stdin=subprocess.PIPE,
                    #stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs)

        self.sock.listen(1)
        logger.debug("Waiting for connection...")
        self.connection, self.client_address = self.sock.accept()
        self.connection_file = self.connection.makefile("r+", bufsize=BUFFER)

    def __del__(self):
        # clean up the process and port
        self.p.terminate()
        self.connection_file.close()
        self.connection.close()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.close()

    @timelimit
    def sendline(self, s, *args, **kwargs):
        """ Send a line by writing a line to the connection_file buffer """
        logger.debug("Sending %r to %s", s, self.shortname)
        self.connection_file.write(s + '\n')
        self.connection_file.flush()
    
    @timelimit
    def readline(self, bts=16,*args, **kwargs):
        """ Read a line from the connection file_handler object """
        msg = self.connection_file.readline()
        logger.debug("Retrieved %r from %s", msg, self.shortname)
        return msg

    def readguess(self, *args, **kwargs):
        """ Read a guess from the player, report as tuple """
        line = self.readline(*args, **kwargs)
        logger.debug("Got raw guess line %s", line)
        try:
            guess = tuple(map(int, line.strip().split(",")))
        except ValueError as e:
            logger.exception("Got a ValueError on our readguess, got %r", line)
            raise
        logger.info("%s guessed %r", self.shortname, guess)
        return guess, line

    def sendguess(self, guess):
        self.sendline("{},{}".format(*guess))

    def readboard(self, *args, **kwargs):
        """ Read an entire board """
        logger.debug("Attempting to read a board from %s", self.shortname)
        boardstrings = []
        for i in xrange(10):
            boardstrings.append( self.readline(1).strip() )
        
        board = {}
        for row,line in enumerate(boardstrings):
            for col,c in enumerate(line):
                if c != "0":
                    board[(row,col)] = c
        return board

class BoardError(Exception):
    def __init__(self, player):
        self.player = player
    def __str__(self):
        return "there was an invalid board reported"


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
        logger.debug("Launching process %s", prog)
        self.p = Process(prog)
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

    def __init__(self, opp0, opp1, pk=0):
        self.pk = pk
        if random.random() < 0.5:
            self.switch = False
        else:
            opp0, opp1 = opp1, opp0
            self.switch = True

        self.p0name = os.path.basename(opp0)
        self.p1name = os.path.basename(opp1)
        self.p0 = BattleshipPlayer(opp0, opp1, 0)
        self.p1 = BattleshipPlayer(opp1, opp0, 1)
        
        self.player_lookup = { self.p0: 0, self.p1: 1}
        
        self.current_player = 0
        self.turns = 0
        self.guesser = self.p0
        self.marker = self.p1

        self.finished = False
        self.winner = 0.5

        self.record = {"player0": self.p0name, "player1": self.p1name, "turns": [], "id": self.pk }

    def __repr__(self):
        return "<BattleshipGame({},{}, turns:{})>".format(self.p0name, self.p1name, self.turns)

    def __del__(self):
        del self.p0
        del self.p1

    def saverecord(self):
        if SAVERECORD:
            recordpath = os.path.join(RECORDPATH, "{}.json".format(self.pk))
            logger.info("Saving record to %s", recordpath)
            with open(recordpath, 'w') as f:
                json.dump(self.record, f, indent=4)

    def _gameinit(self):
        """ Initialize a game and catch errors """
        self.starttime = time.time()
        self.record['starttime'] = self.starttime
        try:
            player = 0
            self.p0.initialize_process()
            player = 1
            self.p1.initialize_process()
            player = 0
            self.p0.read_board()
            self.record["player0board"] = { "{},{}".format(*k):v for k,v in self.p0.board.iteritems() }
            player = 1
            self.p1.read_board()
            self.record["player1board"] = { "{},{}".format(*k):v for k,v in self.p1.board.iteritems() }
            self._validate_boards()
        except BoardError as e:
            logger.exception("Got a board error for player %d", player)
            self.winner = 1-e.player
            self.finished = True
            self.record["error"] = str(e)
            return 1
        except TimeoutError as e:
            logger.exception("Got a timeout error for player %d", player)
            self.winner = 1-player
            self.finished = True
            self.record['error'] = str(e)
            return 1
        return 0

    def turn(self):
        current_actor = self.p0
        turnrec = { "active": self.player_lookup[self.guesser], "starttime": time.time() }
        try:
            # main game loop
            self.turns += 1
            turnrec['turnnum'] = self.turns
            logger.debug("Entering turn %d", self.turns)

            # need to read a guess from the guesser
            current_actor = self.guesser
            guess, line = self.guesser.p.readguess()
            turnrec['guess'] = line

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
                            logger.info("Won the game!")
                            current_actor = self.guesser
                            self.guesser.p.sendline("W")
                            turnrec['response'] = "W"
                            self.winner = 1 - self.turns % 2
                            self.finished = True
                            return
                        else:
                            # sunk a ship, but not dead yet
                            logger.info("Sunk the %r ship", ship)
                            current_actor = self.guesser
                            self.guesser.p.sendline("S{}".format(ship))
                            turnrec['response'] = "S{}".format(ship)
                    else:
                        # just got a hit
                        logger.info("Registered a hit")
                        current_actor = self.guesser
                        self.guesser.p.sendline("H")
                        turnrec['response'] = "H"
                else:
                    # a hit, but already counted
                    logger.info("Registered a REPEATED hit")
                    current_actor = self.guesser
                    self.guesser.p.sendline("H")
                    turnrec['response'] = "H"
            else:
                # we had a miss, send a miss
                if guess not in self.guesser.guesses:
                    logger.info("Miss")
                else:
                    logger.info("REPEATED miss")
                current_actor = self.guesser
                self.guesser.p.sendline("M")
                turnrec['response'] = "M"

            # send the guess to the marker
            if self.finished:
                current_actor = self.marker
                self.marker.p.sendline("L")
                turnrec['notify'] = "L"
            else:
                current_actor = self.marker
                self.marker.p.sendguess(guess)
                turnrec['notify'] = "{},{}\n".format(*guess)

            # swap players
            self.guesser, self.marker = self.marker, self.guesser
        except TimeoutError as e:
            # handle a timeout error
            actorid = self.player_lookup[current_actor]
            logger.exception("Got a timeout player with current actor %d: %s", actorid, current_actor.name)
            # the winner is the non actor
            self.record['error'] = str(e)
            self.winner = 1 - actorid
            self.finished = True
        except ValueError as e:
            # we had a value error trying to read the guess
            actorid = self.player_lookup[current_actor]
            logger.exception("Got a valueerror with current actor %d: %s", actorid, current_actor.name)
            # the winner is the non actor
            self.record['error'] = str(e)
            self.winner = 1 - actorid
            self.finished = True
        except Exception as e:
            # we had some other kind of exception
            self.record['error'] = str(e)
            self.winner = 1 - actorid
            self.finished=True
        finally:
            turnrec['elapsed'] = time.time() - turnrec['starttime']
            self.record['turns'].append(turnrec)

    def game(self):
        """ Run a game from start to finish """
        logger.info("Running a full game: %r", self)

        try: 
            self._gameinit()

            while not self.finished:
                self.turn()

            return self.winner if not self.switch else 1-self.winner
        finally:
            # try to clean up if there was an error
            self.record["time"] = time.time() - self.starttime
            self.record["winner"] = self.winner
            self.record["numturns"] = self.turns

            self.p0.p.p.terminate()
            self.p1.p.p.terminate()

            # self.record['p0stdin'] = self.p0.p.p.stdin.read()
            self.record['p0stdout'] = self.p0.p.p.stdout.read()
            logger.info("p0stdout, %s", self.record['p0stdout'])
            self.record['p0stderr'] = self.p0.p.p.stderr.read()
            logger.info("p0stderr, %s", self.record['p0stderr'])
            # self.record['p1stdin'] = self.p1.p.p.stdin.read()
            self.record['p1stdout'] = self.p1.p.p.stdout.read()
            logger.info("p1stdout, %s", self.record['p1stdout'])
            self.record['p1stderr'] = self.p1.p.p.stderr.read()
            logger.info("p1stderr, %s", self.record['p1stderr'])
            self.saverecord()

            self.p0.p.p.kill()
            self.p1.p.p.kill()


    def _validate_board(self, board):
        """ Validate a single board """
        # First make sure the ship counts are correct
        validcount = Counter(SHIP_LENGTHS)
        count = Counter(board.values())
        if count != validcount:
            logger.warning("Board has an invalid ship count")
            return False
        # now check to make sure each ship is co-linear, and has the right range
        for ship,length in SHIP_LENGTHS.iteritems():
            pairs = [ k for k,v in board.iteritems() if v==ship ]
            xs = [ k[0] for k in pairs ]
            ys = [ k[1] for k in pairs ]

            #colinearity
            if not ( (len(set(xs)) == 1) or (len(set(ys)) == 1) ):
                logger.warning("Board has a non-colinear ship %s", ship)
                return False
            # check to make sure the span of each ship is correct
            if not ( (max(xs)-min(xs) == length-1) or (max(ys)-min(ys) == length-1) ):
                logger.warning("Board has a bad span for ship %s", ship)
                return False

        return True


    def _validate_boards(self):
        """ Check to see if the board is valid
        raise an error if there is a problem with the board"""
        # First try to check to make sure each ship 
        # appears the correct number of times
        if not self._validate_board(self.p0.board):
            logger.warning("Error on player 0 board")
            raise BoardError(0)
        if not self._validate_board(self.p1.board):
            logger.warning("Error on player 1 board")
            raise BoardError(1)

def game(opp0, opp1, pk=0):
    """ Run a single game between two opponents,
        returns either 0 or 1 based on the winner """
    engine = BattleshipGame(opp0, opp1, pk)
    return engine.game()

def unpackgame(opps):
    return game(*opps)

def unpackres(opps):
    out = game(*opps)
    if out == 0:
        result = (opps[0], opps[1])
    else:
        result = (opps[1], opps[0])
    print "{} beat {}".format(result[0], result[1])
    return result

def match(opp0, opp1, N=DEFAULTN):
    """ Run a match between opp0 and opp1, which consists of N games """
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
        return [res for res in executor.map(unpackgame, ((opp0,opp1,i) for i in xrange(N)))]

def getplayers():
    candidates = os.listdir(PLAYERPATH)
    fullpaths = ( os.path.join(PLAYERPATH, p) for p in candidates )
    return [ x for x in fullpaths if os.path.isfile(x) and os.access(x, os.X_OK) ]

def tourney(players=None, N=DEFAULTN):
    """ Run a tournament over all of the players """
    players = players or getplayers() 

    logger.info("Running tournament for %r", players)

    combos = itertools.combinations(players, 2)

    # allgames = []
    gameno = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
        matchups = []
        for combo in combos:
            for i in xrange(N):
                matchups.append((combo[0],combo[1],gameno))
                gameno += 1
        allgames = [res for res in executor.map(unpackres, matchups)]

    return allgames, players

def get_ratings(players=None, N=DEFAULTN):
    """ Run a tournment for all of the players, N times and return the ratings """
    import trueskill

    allgames, players = tourney(players, N)

    ratings = {}
    for p in players:
        ratings[p] = trueskill.Rating()

    logger.info("Calculating ratings...")
    random.shuffle(allgames)
    for winner,loser in allgames:
        ratings[winner], ratings[loser] = trueskill.rate_1vs1(ratings[winner], ratings[loser])

    return ratings, allgames, players


def make_leaderboard(ratings, allgames, players):
    wins = lambda p: sum(1 for g in allgames if g[0]==p)
    loses = lambda p: sum(1 for g in allgames if g[1]==p)

    boardentries = []
    for p in players:
        boardentries.append([os.path.basename(p), ratings[p].exposure, ratings[p].mu, ratings[p].sigma, wins(p), loses(p)])
    
    boardentries = sorted(boardentries, key=lambda x: x[1], reverse=True)
    boardentries = [ [i+1] + x for i,x in enumerate(boardentries) ]
    import tabulate
    table = tabulate.tabulate(boardentries, 
            headers=["rank", "name", "exposure", "mean", "sigma", "wins", "loses"])
    return boardentries, table

def leaderboard(players=None, N=DEFAULTN, filename="leaderboard.txt"):
    """ Create a leaderboard, and optionally save it to a file """
    logger.info("Generating a leaderboard for players: %r, N=%d", players, N)
    ratings, allgames, players = get_ratings(players, N)
    board, table = make_leaderboard(ratings, allgames, players)
    print table
    if filename:
        logger.info("Saving leaderboard to file: %s", filename)
        with open(filename,"w") as f:
            f.write(table)
            f.write('\n')
    return board, table


#---------------------------------------------
# Command line handling
#---------------------------------------------
parser = argparse.ArgumentParser(description="A dirt simple battleship engine.")

parser.add_argument("--leaderboard", '-l', nargs='*', help="Generate the leaderboard")
parser.add_argument("--tournament", '-t', nargs='*', help="Run a tournament between the existing players (or all if empty)")
parser.add_argument("--battle", '-b', nargs=2, help="Run a game between two programs")
parser.add_argument("-n", nargs='?', default=0, type=int, help="The number of games to run")
parser.add_argument("--json","-j", action='store_true', help="Save json output")
parser.add_argument("--workers", "-w", default=WORKERS, help="Number of processes to use")
parser.add_argument("--timeout", type=int, default=TIMEOUT, help="Timeout for each action")
parser.add_argument("--verbose", '-v', default=0, action='count', help="Verbosity for logs")
parser.add_argument("--records", '-r', default=RECORDPATH, help="Path to records")
parser.add_argument("--playerpath", '-p', default=PLAYERPATH, help="Path to players")

if __name__ == "__main__":
    args = parser.parse_args()
   
    # Setup verbosity
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    if args.verbose == 1:
        ch.setLevel(logging.INFO)
    elif args.verbose > 1:
        print "SETTING DEBUG"
        ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("TESTING")

    # handle the big constants
    TIMEOUT = args.timeout
    RECORDPATH = args.records
    PLAYERPATH = args.playerpath
    SAVERECORD = args.json

    # handle the cases
    if args.leaderboard is not None:
        # run a leaderboard, clear all of the records
        records = glob.glob(os.path.join(RECORDPATH,'*.json'))
        for record in records:
            os.remove(record)
        SAVERECORD = True
        leaderboard(players=args.leaderboard, N=args.n or DEFAULTN)
    elif args.tournament is not None:
        print tourney(players=args.tournament, N=args.n or DEFAULTN)
    elif args.battle is not None:
        N = args.n or 1
        for i in xrange(N):
            print "Result for game {}: {}".format(i, game(args.battle[0], args.battle[1]))
    else:
        print "Must choose one of battle, tournament, or leaderboard"
        parser.print_help()
        sys.exit(1)


