#!/usr/bin/env python2
""" 
Author: Alex Alemi

This strategy aims to serve as a simple baseline
We have two modes, hunting and targeting.
If we are hunting, just make a random guess that we have 
never made before.

Anytime we hit, add the north, west, east and south
squares adjacent to a hit to our list of targets, and
enter targetting mode

if in targetting mode, just pop a random target
off the queue and guess it
"""

import logging
import util
import os
import heapq
import socket
import random

# set up simple logging to a file
logging.basicConfig(filename="logs/{}.log".format(os.path.basename(__file__)), level=logging.DEBUG)

comm = util.Communication()

# first we recieve an init string
logging.debug("Recieve the init string...")
initstring = comm.readline()
turn, opponent = initstring.split(",")

if turn=="0":
    myturn = True
else:
    myturn = False
logging.debug("initstring: %s", initstring)


board = util.gen_random_board_str()
for line in board.splitlines():
    comm.sendline(line)

# Now have the main loop, alternating whether its our
# turn or not
guessno = 0

#store whether we are currently hunting or targetting
huntmode = True
# an eventual randomized priority queue that will store our targets
targets = []
guesses = set()
allpos = { (i,j) for i in xrange(10) for j in xrange(10) }

while True:
    try:
        if myturn:
            guessno += 1

            if huntmode:
                guess = random.choice(list(allpos.difference(guesses)))
                logging.debug("Made huntmode guess %r", guess)
            else:
                # we are in targetting mode
                if targets:
                    p, guess = heapq.heappop(targets)
                    logging.debug("Made target mode guess %r", guess)
                else:
                    logging.warning("Seem to have emtpy targets list, fall back to random")
                    guess = random.choice(list(allpos.difference(guesses)))
                    logging.debug("Made (forced) huntmode guess %r", guess)
                if not targets:
                    huntmode = True

            logging.debug("My guess: %r", guess)
            comm.sendline("{},{}".format(*guess))
            guesses.add(guess)

            # and now recieve what happened
            data = comm.readline()
            logging.debug("Got %r", data)
            if data.startswith('H') or data.startswith('S'):
                logging.debug("Got hit or sink, adding targets")
                guessx, guessy = guess
                if guessx > 0:
                    target = (guessx-1, guessy)
                    if target not in guesses:
                        heapq.heappush(targets, (random.random(), target))
                if guessx < 9:
                    target = (guessx+1, guessy)
                    if target not in guesses:
                        heapq.heappush(targets, (random.random(), target))
                if guessy > 0:
                    target = (guessx, guessy-1)
                    if target not in guesses:
                        heapq.heappush(targets, (random.random(), target))
                if guessy < 9:
                    target = (guessx, guessy+1)
                    if target not in guesses:
                        heapq.heappush(targets, (random.random(), target))
                huntmode = False


            myturn = False
        else:
            # if it isn't our turn, we just read our opponents
            # guess
            data = comm.readline()
            logging.debug("got opponent guess: %r", data)
            myturn = True

    except socket.error:
        # the socket closed, we presumably either won or lost
        logging.debug("Socket Closed!")


