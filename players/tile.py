#!/usr/bin/env python2

""" This strategy simply
tries successive guesses, trying to tile
the board, but ignore whether it hits or misses,

this one uses sockets
"""

import logging
import util
import os
import socket

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
while True:
    try:
        if myturn:
            # we need to send a guess
            guessx = guessno % 10
            guessy = (guessno // 10) % 10
            guessno += 1
            logging.debug("My guess: (%d, %d)", guessx, guessy)
            comm.sendline("{},{}".format(guessx, guessy))
        
            # and now recieve what happened
            data = comm.readline()
            logging.debug("Got %r", data)

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


