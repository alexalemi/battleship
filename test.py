#!/usr/bin/env python

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

while True:
    if myturn:
        # we need to send a guess
        guessx = randrange(10)
        guessy = randrange(10)
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



