# Battleship Tournament

A dirt simple [battleship](https://en.wikipedia.org/wiki/Battleship_\(game\))
tournament engine.

The engine expects the processes to communicate over a socket.
When the engine runs your process, it will send a single 
command line argument, which is the port on which you should connect
to.

At that point, the engine will randomly determine who goes first,
and send each program a message on stdin,

    0, opponent_name\n

where the first character tells whether you go first (0) or second (1),
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

The engine will report back on the socket, either `H\n` if a hit,
`M\n` if a miss, `SX\n` if you sunk a ship, where X is one of the 
boat characters above, and `W\n` if you won the game.

If it is not your turn, the engine will notify you of 
your opponents guess in the form a comma separated tuple

    0, 5\n

or, if you just lost, you will recieve a single `L\n`:

## Requirements

if you are running this locally, it uses the following external packages:
    
 * [futures](https://pypi.python.org/pypi/futures)  (e.g. `pip install futures`)
 * [trueskill](https://pypi.python.org/pypi/trueskill/0.4.3) - if you want to generate rankings
