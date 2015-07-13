#!/usr/bin/env python

""" This strategy simply
tries successive guesses, trying to tile
the board, but ignore whether it hits or misses """

import logging
from random import randrange
logging.basicConfig(filename="logs/test.py", level=logging.DEBUG)

# first we recieve an init string
initstring = raw_input()
turn, opponent = initstring.split(",")

if turn=="0":
    myturn = True
else:
    myturn = False
logging.debug("initstring: %s", initstring)

#now we need to send a board
board = ["0000000000", 
        "00000000PP",
        "00B0000000",
        "00B000A000",
        "00B000ASSS",
        "00BDDDA000",
        "000000A000",
        "000000A000",
        "0000000000",
        "0000000000"]

for line in board:
    print line

# Now have the main loop, alternating whether its our
# turn or not

guessno = 0
while True:
    if myturn:
        guessno += 1
        # we need to send a guess
        guessx = guessno % 10
        guessy = guessno // 10
        logging.debug("My guess: (%d, %d)", guessx, guessy)
        print "{},{}".format(guessx, guessy)
    
        # and now recieve what happened
        data = raw_input()
        logging.debug("Got %r", data)

        myturn = False
    else:
        # if it isn't our turn, we just read our opponents
        # guess
        data = raw_input()
        logging.debug("got opponent guess: %r", data)
        myturn = True



