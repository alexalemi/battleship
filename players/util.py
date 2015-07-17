"""
Author: Alex Alemi
Some utility routines for python players
"""
import logging
import socket
import os
import sys
from random import randrange

ship_sizes = {"A": 5, "B": 4, "D": 3, "S": 3, "P": 2}

def board_str(board):
    """ Return the many lined string for a board """
    boardstr = ""
    for i in xrange(10):
        for j in xrange(10):
            if (i,j) in board:
                boardstr += board[(i,j)]
            else:
                boardstr += '0'
        boardstr += '\n'
    return boardstr

def gen_random_board():
    """ Generate a random board """

    def place_ship(board, ship):
        size = ship_sizes[ship]
        orientation = randrange(2)
        if orientation:
            # if we are trying to place it horizontally
            xpos = randrange(10-size)
            ypos = randrange(10)
            for i in xrange(size):
                loc = (xpos+i, ypos)
                if board.get(loc):
                    # we have a collision
                    raise IndexError
                else:
                    board[loc] = ship
        else:
            # if we are trying to place it vertically
            xpos = randrange(10)
            ypos = randrange(10-size)
            for i in xrange(size):
                loc = (xpos, ypos+i)
                if board.get(loc):
                    # we have a collision
                    raise IndexError
                else:
                    board[loc] = ship
        return board

    done = False
    while not done:
        # Generate boards until we manage to not fail
        board = {}
        for ship,size in ship_sizes.iteritems():
            try:
                board = place_ship(board, ship)
            except IndexError:
                break
        else:
            done = True

    return board    

def gen_random_board_str():
    return board_str(gen_random_board())

class LocalCommunication(object):
    """ A very simple local communication thing
        which can be used to locally test your 
        program 
    """
    
    def readline(self):
        msg = raw_input()
        return msg

    def sendline(self,msg):
        print(msg)

class Communication(object):
    """ A simple communication wrapper, use
        
        comm = Communication()
        at which point you can use comm.readline() to read a line
        and comm.sendline(msg) to send a line, sendline 
        will automatically add the newline at the end.
    """
    def __init__(self):
        self.port = int(sys.argv[1])
        logging.debug("Got port %d", self.port)
        # Create the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', self.port)
        logging.debug("Connection to %r", self.server_address)
        self.sock.connect(self.server_address)
        self.sock_file = self.sock.makefile("rw")
        logging.debug("Connected")

    def readline(self):
        msg = self.sock_file.readline()
        logging.debug("Read line %s", msg.strip())
        return msg

    def sendline(self,msg):
        logging.debug("Sending line %s", msg.strip())
        self.sock_file.write(msg + '\n')
        self.sock_file.flush()


