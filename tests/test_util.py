"""Tests for players/util.py"""
import sys
import os

# Add parent directory to path to import players module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'players'))

import util


def test_board_str():
    """Test board_str converts board dict to string correctly"""
    board = {(0, 0): 'A', (0, 1): 'A', (0, 2): 'A', (0, 3): 'A', (0, 4): 'A'}
    result = util.board_str(board)
    lines = result.splitlines()
    assert len(lines) == 10
    assert lines[0] == 'AAAAA00000'
    assert all(line == '0000000000' for line in lines[1:])


def test_gen_random_board():
    """Test random board generation creates valid board"""
    board = util.gen_random_board()

    # Check all ships are present with correct counts
    ship_counts = {}
    for pos, ship in board.items():
        ship_counts[ship] = ship_counts.get(ship, 0) + 1

    assert ship_counts == {'A': 5, 'B': 4, 'D': 3, 'S': 3, 'P': 2}

    # Check all positions are valid
    for row, col in board.keys():
        assert 0 <= row < 10
        assert 0 <= col < 10


def test_gen_random_board_str():
    """Test random board string generation"""
    board_str = util.gen_random_board_str()
    lines = board_str.splitlines()

    assert len(lines) == 10
    assert all(len(line) == 10 for line in lines)

    # Count ships in the board string
    all_chars = ''.join(lines)
    assert all_chars.count('A') == 5
    assert all_chars.count('B') == 4
    assert all_chars.count('D') == 3
    assert all_chars.count('S') == 3
    assert all_chars.count('P') == 2
    assert all_chars.count('0') == 100 - 17  # 83 empty squares
