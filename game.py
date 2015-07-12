"""
Run a game of battleship between two processes.

to run, give the names of the two binaries to execute.
 e.g. python game.py /path/to/engine1 /path/to/engine2

At that point, the engine will randomly determine who goes first,
and send each engine a message on stdin,

  0, opponent_name

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

    0000000000
    00000000PP
    00B0000000
    00B000A000
    00B000ASSS
    00BDDDA000
    000000A000
    000000A000
    0000000000
    0000000000

At that point, if it is your turn, you must report your guess
as a comma separated tuple, 0-indexed, e.g.

    0, 5

The engine will report back on stdin, either H if a hit,
M if a miss, SX if you sunk a ship, where X is one of the 
boat characters above, and W if you won the game.

If it is not your turn, the engine will notify you of 
your opponents guess in the form a comma separated tuple

  0, 5

"""

import sys

def game(opp1, opp2):
    """ Run a game between two opponents """

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
    else:
        opp1 = sys.argv[1]
        opp2 = sys.argv[2]
        run_game(opp1, opp2)
