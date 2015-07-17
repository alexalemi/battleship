#!/usr/bin/env pypy3

import random
import logging
import sys
import util
logging.basicConfig(filename="logs/frederic.log", level=logging.DEBUG)
comm = util.Communication()

blah_file = open("blah", "w")

rows = 10
cols = 10
NUM_ITERATIONS = 1000

codes = {'A': 1, 'B' : 2, 'S': 3, 'D': 4, 'P': 5, 'H' : 6, 'M': 7}
sunk = 8
def is_sunken(code):
    return code & sunk == sunk
def ship_name(code):
    for name,code_num in codes.items():
        if code_num == code:
            return name
    return '0'
# sorted by descending length
pieces = [(codes['A'], 5),
          (codes['B'], 4),
          (codes['S'], 3),
          (codes['D'], 3),
          (codes['P'], 2)]

def construct_board(positions):
    board = [[0 for c in range(cols)] for r in range(rows)]
    invalid = False
    def try_update(x, y, value):
        nonlocal invalid
        nonlocal board
        if board[x][y] != 0:
            invalid = True
        board[x][y] = value
    for name,size,orientation,x,y in positions:
        if orientation == 0: #down
            for xp in range(x,x + size):
                try_update(xp,y, name)
        else:
            for yp in range(y, y + size):
                try_update(x, yp, name)
    return (board, invalid)                

def valid_board(positions):
    board, invalid = construct_board(positions)
    return not invalid

def print_board(board,out_file=sys.stdout):
    for r in range(rows):
        for c in range(cols):
            print(ship_name(board[r][c]) , end="",file=out_file)
        print("", file=out_file)
        
def out_board(board,out_file=sys.stdout):
    for r in range(rows):
        line = ""
        for c in range(cols):
            line = line + ship_name(board[r][c])
        comm.sendline(line)

def generate_board_uniformly():
    while True:
        positions = []
        for name,size in pieces:
            orientation = random.randrange(0, 2)
            if orientation == 0: # down
                x = random.randint(0, rows - size)
                y = random.randrange(0, cols)
            else:
                x = random.randrange(0, rows)
                y = random.randint(0, cols - size)
            positions.append((name, size, orientation, x, y))
        #if valid_board(positions):
        board, invalid = construct_board(positions) 
        if not invalid: return board

def no_string(string, twod_array):
    for x in range(len(twod_array)):
        for y in range(len(twod_array[x])):
            if twod_array[x][y] == string:
                return False
    return True
        
def generate_board_uniformly_withconstraints(known,sunken):
    def check(x, y):
        nonlocal known
#        print (x,y)
        return known[x][y] == codes["H"] or known[x][y] == 0
    possible = {}
    remaining_pieces = [(name,size)
                        for (name,size) in pieces
                        if no_string(sunk | name, known)]
    for name,size in remaining_pieces:
        possible[name] = []
        # down
        for x in range(0, rows - size + 1):
            for y in range(0, cols):
                valid = True
                orientation = 0
                hit_sunk = False
                sunken_count = 0
                for xp in range(x,x + size):
                    valid = valid and check(xp,y)
                    if known[x][y] != 0 and is_sunken(known[x][y]):
                        sunken_count += 1
                if sunken_count != 0: valid = False
                if valid:
                    possible[name].append(
                        (name, size, orientation, x, y))
        for x in range(0, rows):
            for y in range(0, cols - size + 1):
                valid = True
                orientation = 1
                for yp in range(y, y + size):
                    valid = valid and check(x,yp)
                if valid:
                    possible[name].append(
                        (name, size, orientation, x, y))
        
    while True:
        positions = []
        for name,size in remaining_pieces:
            choice = random.randrange(0, len(possible[name]))
            positions.append(possible[name][choice])
        for name,options in sunken:
            choice = random.randrange(0, len(options))
            positions.append(options[choice])
        positions = positions
        board, invalid = construct_board(positions)
        if not invalid: return board
#        logging.debug("failed to generate.")
        #print_board(board,out_file=blah_file)
        #print("",file=blah_file)

def count_inconsistencies(known, board):
    count = 0
    for r in range(rows):
        for c in range(cols):
            if known[r][c] == codes['M'] and board[r][c] != 0:
                count += 1
                logging.debug("BADBADBAD")
                # shouldn't happen anymore
            elif known[r][c] != 0 and known[r][c] != codes['M'] and board[r][c] == 0:
                count += 1
    return count
        
# shitty strategy
def pick_move(known, num_turns, sunken):
    scores = [[0 for c in range(cols)] for r in range(rows)]
    for i in range(NUM_ITERATIONS):
        random_board = generate_board_uniformly_withconstraints(known, sunken)
        number_of_errors = count_inconsistencies(known,random_board)
        penalty = 4 ** (-number_of_errors)
        for r in range(rows):
            for c in range(cols):
                if known[r][c] != 0:
                    pass
#                    logging.debug("Ignore: {}".format((r,c)))
                else:
                    scores[r][c] += penalty * (random_board[r][c] != 0)
    best_r = 0
    best_c = 0
    for r in range(rows):
        for c in range(cols):
            if scores[r][c] > scores[best_r][best_c]:
                best_r, best_c = r, c
    logging.debug(scores[best_r][best_c])
#    if known[best_r][best_c] != 0:
#        logging.debug("oops.")
    return (best_r, best_c)

def possible_places_sunken(known, sunken, x0, y0):
    """List of places ship could have sunk."""
    remaining_pieces = [(name,size)
                        for (name,size) in pieces
                        if no_string(sunk | name, known)]
    name = known[x0][y0] & ~sunk
    known[x0][y0] = codes["H"] # temporary
    size = 0
    for n,s in pieces:
        if name == n:
            size = s
    def check(x, y):
        nonlocal known
#        print (x,y)
        return known[x][y] == codes["H"]
    possible = []
    # fixed column
    y = y0
    for x in range(max(0, x0 - size + 1), min(rows - size + 1, x0 + 1)):
        valid = True
        orientation = 0
        for xp in range(x,x + size):
            valid = valid and check(xp,y)
        if valid:
            possible.append(
                (name, size, orientation, x, y))
    # fixed row
    x = x0
    for y in range(max(0, y0 - size + 1), min(cols - size + 1, y0 + 1)):
        valid = True
        orientation = 1
        for yp in range(y, y + size):
            valid = valid and check(x,yp)
        if valid:
            possible.append(
                (name, size, orientation, x, y))
    known[x0][y0] = name | sunk
    return possible
#    answer = possible[0]
#    sunken.append(answer)
#    (name, size, orientation, x, y) = answer
#    if orientation == 0: #vertical
#        for xp in range(x,x + size):
#            known[xp][y] = "S" + name
#    else:
#        for yp in range(y, y + size):
#            known[x][yp] = "S" + name
    
if __name__ == "__main__":
    # first we recieve an init string
    initstring = comm.readline()
    turn, opponent = initstring.split(",")

    if turn=="0":
        myturn = True
    else:
        myturn = False

    my_board = generate_board_uniformly()
    out_board(my_board)

    known = [[0 for c in range(cols)] for r in range(rows)]
    num_turns = 0
    sunken = []
    while True:
        num_turns += 1
        if myturn:
            guessx,guessy = pick_move(known, num_turns, sunken)
            # we need to send a guess
            #logging.debug("My guess: (%d, %d)", guessx, guessy)
            comm.sendline("{},{}".format(guessx, guessy))
    
            # and now recieve what happened
            data = comm.readline()
            #logging.debug("Got %r", data)

            # H or M or S(ship)
            if data[0] == "S":
                known[guessx][guessy] = codes[data[1]] | sunk
            elif data[0] != "W" and data[0] != "L":
                known[guessx][guessy] = codes[data[0]]
            if data[0] == "S":
                possible_places = possible_places_sunken(known, sunken,
                                                         guessx, guessy)
                sunken.append((data[1], possible_places))
            print_board(known,out_file=blah_file)
            print("",file=blah_file)
            blah_file.flush()
#            print_board(known)
            
            myturn = False
        else:
            # if it isn't our turn, we just read our opponents
            # guess
            data = comm.readline()
            # who cares what it is???
            # only needed if we need to estimate remaining
            # number of turns
            #        logging.debug("got opponent guess: %r", data)
            myturn = True

    
