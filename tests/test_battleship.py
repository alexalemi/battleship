"""Tests for battleship.py"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import battleship


def test_ship_lengths():
    """Test SHIP_LENGTHS constant is correct"""
    assert battleship.SHIP_LENGTHS == {"A": 5, "B": 4, "D": 3, "S": 3, "P": 2}


def test_validate_board_valid():
    """Test board validation with a valid board"""
    game = battleship.BattleshipGame.__new__(battleship.BattleshipGame)

    # Create a valid board
    valid_board = {
        (0, 0): 'A', (0, 1): 'A', (0, 2): 'A', (0, 3): 'A', (0, 4): 'A',  # Aircraft carrier
        (1, 0): 'B', (1, 1): 'B', (1, 2): 'B', (1, 3): 'B',  # Battleship
        (2, 0): 'D', (2, 1): 'D', (2, 2): 'D',  # Destroyer
        (3, 0): 'S', (3, 1): 'S', (3, 2): 'S',  # Submarine
        (4, 0): 'P', (4, 1): 'P',  # Patrol boat
    }

    assert game._validate_board(valid_board) is True


def test_validate_board_invalid_count():
    """Test board validation rejects incorrect ship counts"""
    game = battleship.BattleshipGame.__new__(battleship.BattleshipGame)

    # Board with too many A's
    invalid_board = {
        (0, 0): 'A', (0, 1): 'A', (0, 2): 'A', (0, 3): 'A', (0, 4): 'A', (0, 5): 'A',
    }

    assert game._validate_board(invalid_board) is False


def test_validate_board_non_colinear():
    """Test board validation rejects non-colinear ships"""
    game = battleship.BattleshipGame.__new__(battleship.BattleshipGame)

    # L-shaped ship (invalid)
    invalid_board = {
        (0, 0): 'A', (0, 1): 'A', (0, 2): 'A', (1, 2): 'A', (2, 2): 'A',
        (1, 0): 'B', (1, 1): 'B', (2, 1): 'B', (3, 1): 'B',
        (2, 0): 'D', (3, 0): 'D', (4, 0): 'D',
        (5, 0): 'S', (5, 1): 'S', (5, 2): 'S',
        (6, 0): 'P', (6, 1): 'P',
    }

    assert game._validate_board(invalid_board) is False


def test_validate_board_wrong_span():
    """Test board validation rejects ships with gaps"""
    game = battleship.BattleshipGame.__new__(battleship.BattleshipGame)

    # Ship with a gap
    invalid_board = {
        (0, 0): 'A', (0, 1): 'A', (0, 2): 'A', (0, 3): 'A', (0, 5): 'A',  # Gap at (0,4)
        (1, 0): 'B', (1, 1): 'B', (1, 2): 'B', (1, 3): 'B',
        (2, 0): 'D', (2, 1): 'D', (2, 2): 'D',
        (3, 0): 'S', (3, 1): 'S', (3, 2): 'S',
        (4, 0): 'P', (4, 1): 'P',
    }

    assert game._validate_board(invalid_board) is False
