# Battleship Tournament

A modern Python battleship tournament engine for hosting AI bot competitions.

[![CI](https://github.com/yourusername/battleship/workflows/CI/badge.svg)](https://github.com/yourusername/battleship/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- **Socket-based communication** between tournament engine and player bots
- **TrueSkill ranking system** for competitive leaderboards
- **Parallel game execution** for fast tournament completion
- **JSON game recording** for replay and analysis
- **Static website generation** for results visualization
- **Modern Python 3.8+** with type hints and comprehensive tests

## Installation

### Requirements

- Python 3.8 or higher
- pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/battleship.git
cd battleship

# Install the package and dependencies
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

## Usage

The battleship tournament engine supports three main modes:

### 1. Single Battle

Run a single game between two player bots:

```bash
battleship --battle players/hunter.py players/randguess.py

# Run multiple games
battleship --battle players/hunter.py players/randguess.py -n 10
```

### 2. Tournament

Run a round-robin tournament between all players (or specific players):

```bash
# Tournament with all players
battleship --tournament

# Tournament with specific players
battleship --tournament players/hunter.py players/ethan.py players/maxime.py

# Specify number of games per matchup
battleship --tournament -n 50
```

### 3. Leaderboard

Generate a full tournament with TrueSkill rankings:

```bash
# Generate leaderboard for all players
battleship --leaderboard

# Generate leaderboard for specific players
battleship --leaderboard players/hunter.py players/ethan.py

# Specify number of games per matchup
battleship --leaderboard -n 100
```

### Additional Options

```bash
# Save game records as JSON
battleship --leaderboard -j --records ./my_records

# Use custom player directory
battleship --tournament -p ./my_players

# Adjust parallelism (default: 2 workers)
battleship --tournament -w 4

# Set move timeout in seconds (default: 2)
# IMPORTANT: Use --timeout 5 for maxime.py which is computationally intensive
battleship --tournament --timeout 5

# Verbose logging
battleship --battle players/hunter.py players/randguess.py -vv
```

### Performance Note

Some player bots are computationally intensive:
- **maxime.py** (~1.9s per move) - Requires `--timeout 5` or higher
- **frederic.py** (~0.5s per move) - Works with default timeout
- **Other bots** (<0.1s per move) - Very fast

See [PERFORMANCE.md](PERFORMANCE.md) for detailed performance information and tournament duration estimates.

## Communication Protocol

The engine communicates with player bots via TCP sockets. When the engine launches your bot, it provides a port number as a command-line argument.

### Initialization

1. **Connect** to `localhost:<port>` via TCP socket
2. **Receive** initialization message: `{0|1}, {opponent_name}\n`
   - `0` = you go first
   - `1` = you go second
3. **Send** your 10x10 board as 10 lines of 10 characters:
   - `A` = Aircraft carrier (length 5)
   - `B` = Battleship (length 4)
   - `S` = Submarine (length 3)
   - `D` = Destroyer (length 3)
   - `P` = Patrol boat (length 2)
   - `0` = Empty square

Example board:

```
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
```

### Game Loop

**When it's your turn:**
- **Send** your guess as `x,y\n` (0-indexed coordinates)
- **Receive** response:
  - `H\n` = Hit
  - `M\n` = Miss
  - `SX\n` = Sunk ship X (where X is A/B/S/D/P)
  - `W\n` = You won

**When it's opponent's turn:**
- **Receive** opponent's guess as `x,y\n`
- Continue until game ends with `L\n` (you lost)

## Writing a Player Bot

### Using the Utility Module

The `players/util.py` module provides helper functions:

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import util
import random

# Initialize communication
comm = util.Communication()

# Read initialization
initstring = comm.readline()
turn, opponent = initstring.split(",")
myturn = (turn == "0")

# Generate and send board
board_str = util.gen_random_board_str()
for line in board_str.splitlines():
    comm.sendline(line)

# Track guesses
guesses = set()
allpos = {(i, j) for i in range(10) for j in range(10)}

# Game loop
while True:
    if myturn:
        # Make a guess
        guess = random.choice(list(allpos.difference(guesses)))
        guesses.add(guess)
        comm.sendline(f"{guess[0]},{guess[1]}")

        # Read response
        response = comm.readline()
        # Process response...

        myturn = False
    else:
        # Read opponent's guess
        data = comm.readline()
        myturn = True
```

### Strategy Examples

The repository includes several example strategies:

- **ethan.py** - Advanced probabilistic strategy (90% win rate)
- **maxime.py** - Monte Carlo simulation approach
- **frederic.py** - Board evaluation with bit-encoded states
- **hunter.py** - Hunt-and-target baseline strategy
- **hunter_parity.py** - Hunt-and-target with parity optimization
- **tile.py** - Sequential tiling (weak baseline)
- **randguess.py** - Pure random guessing (weakest)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_util.py -v
```

### Code Quality

This project uses modern Python tooling:

```bash
# Format code with black
black .

# Lint with ruff
ruff check .

# Type check with mypy
mypy battleship.py website.py players/util.py

# Install pre-commit hooks
pre-commit install

# Run all pre-commit checks
pre-commit run --all-files
```

### Project Structure

```
battleship/
├── battleship.py          # Main tournament engine
├── website.py             # Static site generator
├── pyproject.toml         # Project configuration
├── players/               # Player bot implementations
│   ├── util.py           # Shared utilities
│   ├── ethan.py          # Advanced strategy
│   ├── hunter.py         # Hunt-and-target
│   └── ...
├── tests/                 # Test suite
│   ├── test_battleship.py
│   └── test_util.py
├── templates/             # Jinja2 templates
├── .github/
│   └── workflows/
│       └── ci.yml        # GitHub Actions CI
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-strategy`)
3. Make your changes and add tests
4. Ensure tests pass and code is formatted (`pytest && black .`)
5. Commit your changes (`git commit -m 'Add amazing strategy'`)
6. Push to the branch (`git push origin feature/amazing-strategy`)
7. Open a Pull Request

## Acknowledgments

Original author: Alex Alemi (2015)
Modernized: 2025

---

## Tournament Results

See the [leaderboard.txt](leaderboard.txt) file for current rankings!

Current champion: **ethan.py** with a 90% win rate (135-15 record)
