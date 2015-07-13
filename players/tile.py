#!/usr/bin/env python2

""" This strategy simply
tries successive guesses, trying to tile
the board, but ignore whether it hits or misses,

this one uses sockets
"""

import logging
import socket
import os
import sys

from random import randrange

BUFFER = 2048

# set up simple logging to a file
logging.basicConfig(filename="logs/{}.log".format(os.path.basename(__file__)), level=logging.DEBUG)

# Read in the port we should connect on
port = int(sys.argv[1])
logging.debug("Got port %d", port)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', port)
logging.debug("Connection to %r", server_address)
sock.connect(server_address)
sock_file = sock.makefile("+", bufsize=BUFFER)
logging.debug("Connected")

def readline():
    msg = sock_file.readline()
    return msg

def sendline(msg):
    sock_file.write(msg + '\n')
    sock_file.flush()

# first we recieve an init string
logging.debug("Recieve the init string...")
initstring = readline()
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
    sendline(line)

# Now have the main loop, alternating whether its our
# turn or not

guessno = 0
while True:
    try:
        if myturn:
            guessno += 1
            # we need to send a guess
            guessx = guessno % 10
            guessy = guessno // 10
            logging.debug("My guess: (%d, %d)", guessx, guessy)
            sendline("{},{}".format(guessx, guessy))
        
            # and now recieve what happened
            data = readline()
            logging.debug("Got %r", data)

            myturn = False
        else:
            # if it isn't our turn, we just read our opponents
            # guess
            data = readline()
            logging.debug("got opponent guess: %r", data)
            myturn = True
    except socket.error:
        # the socket closed, we presumably either won or lost
        logging.debug("Socket Closed!")


