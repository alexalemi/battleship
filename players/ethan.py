#! /usr/bin/env python
####################################################################################################
# SET UP
#
#

# TODO: Probabilistic Guess Function
# TODO: Account for likelihood that ships are not adjacent
# TODO: Minimize Entropy Model

import socket
import time
import util
from copy import copy

ascii_board = 'A00000000B\nA00000000B\nA00000000B\nA00000000B\nA000000000\n0000000000\n0000000000\n0000000000\nP000000000\nP00DDD0SSS\n'

TEST_BOARD = [['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','P','?','?','?','?','?'],
			  ['?','?','?','?','P','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?'],
			  ['?','?','?','?','?','?','?','?','?','?']]

BOARD = [['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?'],
		 ['?','?','?','?','?','?','?','?','?','?']]

NON_HUMAN_OPPONENTS = ['players/hunter_parity.py',
					   'players/hunter.py',
					   'players/randguess.py',
					   'players/tile.py']
SHIPS = ['A', 'B', 'D', 'P', 'S']
SHIP_SIZE = {'A':5, 'B':4, 'D':3, 'P':2, 'S':3}

####################################################################################################
# UTILITY FUNCTIONS
#
#

def read_board(ascii_board):
	"""
	Reads in a board from a ascii format as a board of array of arrays format
	"""
	board = []
	row = []
	col_num = 0
	for char in ascii_board:
		if(col_num < 10):
			row.append(char)
			col_num += 1
		else:
			board.append(row)
			row = []
			col_num = 0
	return board

def print_board(board):
	"""
	Prints a board neatly
	"""
	for row in board:
		for index in range(len(row)):
			if(isinstance(row[index], int)):
				if(row[index] < 10):
					row[index] = ' ' + str(row[index])
				else:
					row[index] = str(row[index])
		print(row)

def is_valid(row, col):
	"""
	Returns a boolean based on whether on not a (row, col) pair is a valid board coordinate
	"""
	return ((row >= 0) and (row <= 9) and (col >= 0) and (col <= 9))

def copy_of(board):
	"""
	Returns a copy of a board
	"""
	copy = []
	for row_num in range(10):
		row = []
		for col_num in range(10):
			row.append(board[row_num][col_num])
		copy.append(row)
	return copy

def generate_question_mark_board():
	"""
	Retruns a board filled with question marks
	"""
	board = []
	for row in range(10):
		row = []
		for col in range(10):
			row.append('?')
		board.append(row)
	return board

def generate_scoring_board():
	"""
	Generates a board of values used to score your arrangement of ships
	"""
	scoring_board = board_possibility_counter(BOARD)
	max_possibilites = scoring_board[4][4]
	for row in range(10):
		for col in range(10):
			scoring_board[row][col] = max_possibilites - scoring_board[row][col]
	return scoring_board

def generate_playing_board(duration):
	"""
	Generates a random playing board
	"""
	timeout = time.time() + duration
	random_board_string = util.gen_random_board_str()
	max_score = score(read_board(random_board_string))
	while time.time() < timeout:
		new_random_board_string = util.gen_random_board_str()
		new_score = score(read_board(new_random_board_string))
		if new_score > max_score:
			random_board_string = new_random_board_string
			max_score = new_score
			print max_score
	return random_board_string

def x_in_board(board):
	"""
	Determines whether or not there is a hit but unsunk ship in board
	"""
	for row in range(10):
		for col in range(10):
			if(board[row][col] == 'X'):
				return True
	return False

def smallest_ship_size(ships):
	"""
	Returns the size of the smallest ship in a given list of ships
	"""
	if len(ships) != 0:
		ship_sizes = []
		for ship in ships:
			ship_sizes.append(SHIP_SIZE[ship])
		return min(ship_sizes)
	else:
		return max(SHIP_SIZE.values())

def unsunk_ships(board):
	"""
	Returns a list of the ships that have not yet been sunk
	"""
	ships = SHIPS
	for row in range(10):
		for col in range(10):
			if(board[row][col] in ships):
				ships.remove(board[row][col])
	return ships

def surrounding_unsunk_hits(board, row, col):
	"""
	Return the coordinates of all surrounding X's
	"""
	unsunk_hits = []
	if(is_valid(row - 1, col)):
		if(board[row - 1][col] == 'X'):
			unsunk_hits.append((row - 1, col))
	if(is_valid(row + 1, col)):
		if(board[row + 1][col] == 'X'):
			unsunk_hits.append((row + 1, col))
	if(is_valid(row, col - 1)):
		if(board[row][col - 1] == 'X'):
			unsunk_hits.append((row, col - 1))
	if(is_valid(row, col + 1)):
		if(board[row][col + 1] == 'X'):
			unsunk_hits.append((row, col + 1))
	return unsunk_hits

def count_unknown_spaces(board, row, col, direction):
	"""
	Counts the number (up to 4) of '?' spaces in any given direction ('up', 'down', 'left', 'right')
	From the (row, col) space on the board
	"""
	unknown = 0
	shift = 1

	if(direction == 'left'):
		while(is_valid(row, col - shift)):
			if(board[row][col - shift] != '?'):
				break
			unknown += 1
			shift += 1

	elif(direction == 'right'):
		while(is_valid(row, col + shift)):
			if(board[row][col + shift] != '?'):
				break
			unknown += 1
			shift += 1

	elif(direction == 'up'):
		while(is_valid(row - shift, col)):
			if(board[row - shift][col] != '?'):
				break
			unknown += 1
			shift += 1

	elif(direction == 'down'):
		while(is_valid(row + shift, col)):
			if(board[row + shift][col] != '?'):
				break
			unknown += 1
			shift += 1

	return unknown

def sunken_ship_update(board, row, col, ship):
	"""
	Returns the direction from (row, col) that the specified newly sunken ship is
	"""
	updated_board = copy_of(board)
	# Check Left
	flag = True
	for shift in range(SHIP_SIZE[ship]):
		if(is_valid(row, col - shift) == False):
			flag = False
			break
		elif(board[row][col - shift] != 'X'):
			flag = False
			break
		else:
			updated_board[row][col - shift] = ship
	if(flag == True):
		return updated_board
	else:
		updated_board = copy_of(board)

	# Check Right
	flag = True
	for shift in range(SHIP_SIZE[ship]):
		if(is_valid(row, col + shift) == False):
			flag = False
			break
		elif(board[row][col + shift] != 'X'):
			flag = False
			break
		else:
			updated_board[row][col + shift] = ship
	if(flag == True):
		return updated_board
	else:
		updated_board = copy_of(board)

	# Check Up
	flag = True
	for shift in range(SHIP_SIZE[ship]):
		if(is_valid(row - shift, col) == False):
			flag = False
			break
		elif(board[row - shift][col] != 'X'):
			flag = False
			break
		else:
			updated_board[row - shift][col] = ship
	if(flag == True):
		return updated_board
	else:
		updated_board = copy_of(board)

	# Check Down
	flag = True
	for shift in range(SHIP_SIZE[ship]):
		if(is_valid(row + shift, col) == False):
			flag = False
			break
		elif(board[row + shift][col] != 'X'):
			flag = False
			break
		else:
			updated_board[row + shift][col] = ship
	if(flag == True):
		return updated_board
	else:
		updated_board = copy_of(board)

	return updated_board


####################################################################################################
# CALCULATION FUNCTIONS
#
#

def score(board):
	"""
	Returns the score of a board according to the scoring board
	"""
	scoring_board = generate_scoring_board()
	score = 0
	for row in range(10):
		for col in range(10):
			if board[row][col] != '0':
				score += scoring_board[row][col]
	return score

def line_possibility_counter(spaces1, spaces2, given_spaces, ships):
	"""
	Counts the number of possible ways to place ships in a horizontal line from a given space,
	Given that there are spaces1 unknown spaces on one side, spaces2 unknown spaces on the other side,
	and the array of ships currently still unsunk
	"""
	count = 0
	for ship in ships:
		count += single_ship_line_possibility_counter(spaces1, spaces2, given_spaces, ship)
	return count

def single_ship_line_possibility_counter(spaces1, spaces2, given_spaces, ship):
	"""
	Counts the number of possible ways to place a single ship in a horizontal line from a given space,
	Given that there are spaces1 unknown spaces on one side, spaces2 unknown spaces on the other side
	"""
	ship_size = SHIP_SIZE[ship]
	free_spaces = ship_size - given_spaces
	if(spaces1 > free_spaces):
		spaces1 = free_spaces
	if(spaces2 > free_spaces):
		spaces2 = free_spaces
	if(spaces1 + spaces2 - free_spaces + 1 > 0):
		return spaces1 + spaces2 - free_spaces + 1
	else:
		return 0

def board_possibility_counter(board):
	"""
	Counts the number of ways ships can be placed in each spot in a given board
	"""
	counts_board = []
	for row in range(10):
		counts_row = []
		for col in range(10):
			count = 0
			if(board[row][col] == '?'):
				ships = unsunk_ships(board)
				left_unknown = count_unknown_spaces(board, row, col, 'left')
				right_unknown = count_unknown_spaces(board, row, col, 'right')
				up_unknown = count_unknown_spaces(board, row, col, 'up')
				down_unknown = count_unknown_spaces(board, row, col, 'down')
				count += line_possibility_counter(left_unknown, right_unknown, 1, ships)
				count += line_possibility_counter(up_unknown, down_unknown, 1, ships)
			counts_row.append(count)
		counts_board.append(counts_row)
	return counts_board

####################################################################################################
# MOVE GUESSING FUNCTIONS
#
#

def guess(their_board):
	"""
	Returns a calculated guess based on the opponent's board
	"""
	board = board_possibility_counter(their_board)
	ships_remaining = unsunk_ships(board)
	min_size = smallest_ship_size(ships_remaining)
	max_coords = (0, 0)
	for row in range(10):
		for col in range(10):
			if(((row + col) % min_size) == 0):
				if(board[row][col] > board[max_coords[0]][max_coords[1]]):
					max_coords = (row, col)
	return max_coords

def target_helper(board, line_type, num, ships):
	"""
	Returns a targeted guess for when there have been hits but no sink
	Only searches a single row (line_type = 'row') or column (line_type = 'col')
	"""
	possibilities_map = {}
	if(line_type == 'row'):
		left_hit_col = -1
		right_hit_col = -1
		for col in range(10):
			if(board[num][col] == 'X'):
				# Set start col of hits in row (if applicable)
				if(is_valid(num, col - 1)):
					if(board[num][col - 1] != 'X'):
						left_hit_col = col - 1
				# Set end col of hits in row (if applicable)
				if(is_valid(num, col + 1)):
					if(board[num][col + 1] != 'X'):
						right_hit_col = col + 1

		left_hit_ways = 0
		right_hit_ways = 0
		given_spaces = right_hit_col - left_hit_col
		in_a_row_bonus = 1
		if(given_spaces >= 3):
			in_a_row_bonus = 100

		if(is_valid(num, left_hit_col)):
			if(board[num][left_hit_col] == '?'):
				left_unknown = count_unknown_spaces(board, num, left_hit_col, 'left')
				right_unknown = count_unknown_spaces(board, num, right_hit_col - 1, 'right')
				left_hit_ways = line_possibility_counter(left_unknown, right_unknown, given_spaces, ships)
				possibilities_map[(num, left_hit_col)] = in_a_row_bonus + left_hit_ways

		if(is_valid(num, right_hit_col)):
			if(board[num][right_hit_col] == '?'):
				left_unknown = count_unknown_spaces(board, num, left_hit_col + 1, 'left')
				right_unknown = count_unknown_spaces(board, num, right_hit_col, 'right')
				right_hit_ways = line_possibility_counter(left_unknown, right_unknown, given_spaces, ships)
				possibilities_map[(num, right_hit_col)] = in_a_row_bonus + right_hit_ways

	elif(line_type == 'col'):
		up_hit_row = -1
		down_hit_row = -1
		for row in range(10):
			if(board[row][num] == 'X'):
				# Set start col of hits in row (if applicable)
				if(is_valid(row - 1, num)):
					if(board[row - 1][num] != 'X'):
						up_hit_row = row - 1
				# Set end col of hits in row (if applicable)
				if(is_valid(row + 1, num)):
					if(board[row + 1][num] != 'X'):
						down_hit_row = row + 1

		up_hit_ways = 0
		down_hit_ways = 0
		given_spaces = down_hit_row - up_hit_row
		in_a_row_bonus = 1
		if(given_spaces >= 3):
			in_a_row_bonus = 100

		if(is_valid(up_hit_row, num)):
			if(board[up_hit_row][num] == '?'):
				up_unknown = count_unknown_spaces(board, up_hit_row, num, 'up')
				down_unknown = count_unknown_spaces(board, down_hit_row - 1, num, 'down')
				up_hit_ways = line_possibility_counter(up_unknown, down_unknown, given_spaces, ships)
				possibilities_map[(up_hit_row, num)] = in_a_row_bonus + up_hit_ways

		if(is_valid(down_hit_row, num)):
			if(board[down_hit_row][num] == '?'):
				up_unknown = count_unknown_spaces(board, up_hit_row + 1, num, 'up')
				down_unknown = count_unknown_spaces(board, down_hit_row, num, 'down')
				down_hit_ways = line_possibility_counter(up_unknown, down_unknown, given_spaces, ships)
				possibilities_map[(down_hit_row, num)] = in_a_row_bonus + down_hit_ways

	return possibilities_map

def target(board):
	"""
	Returns a targeted guess given a board with hit but unsunk ships
	"""
	# TODO: Have targeted guesses prefer a specific parity and/or squares with high guess index
	possibilities_map = {}
	ships = unsunk_ships(board)
	for row in range(10):
		row_map = target_helper(board, 'row', row, ships)
		for coords in row_map:
			if(coords in possibilities_map):
				possibilities_map[coords] += row_map[coords]
			else:
				possibilities_map[coords] = row_map[coords]
	for col in range(10):
		col_map = target_helper(board, 'col', col, ships)
		for coords in col_map:
			if(coords in possibilities_map):
				possibilities_map[coords] += col_map[coords]
			else:
				possibilities_map[coords] = col_map[coords]
	target_coords = max(possibilities_map, key=possibilities_map.get)
	# return possibilities_map
	return target_coords

def fire(board):
	"""
	Returns the move for the turn
	"""
	if(x_in_board(board)):
		return target(board)
	else:
		return guess(board)

def update_board(board, row, col, last_fire_result):
	"""
	Returns an updated game board based on the last_fire_result
	"""
	updated_board = copy_of(board)
	if(last_fire_result == 'M'):
		updated_board[row][col] = '0'
	elif(last_fire_result == 'H'):
		updated_board[row][col] = 'X'
	elif last_fire_result.startswith('S'):
		updated_board[row][col] = 'X'
		updated_board = sunken_ship_update(updated_board, row, col, last_fire_result[1])
	return updated_board
	
def play_game():
	"""
	Plays a full game of battleship against an opponent
	"""
	board = copy_of(BOARD)
	comm = util.Communication()
	initstring = comm.readline()
	turn, opponent = initstring.split(",")
	opponent = opponent.strip()

	# Generate and send my board
	if opponent in NON_HUMAN_OPPONENTS:
		genboard = ascii_board
	else:
		genboard = generate_playing_board(1.95)
	for line in genboard.splitlines():
	    comm.sendline(line)

	if turn == "0":
	    myturn = True
	else:
	    myturn = False

	guesses = set()

	while True:
		try:
			if myturn:
				# Send a guess
				guess = fire(board)
				guessx, guessy = guess
				guesses.add(guess)
				comm.sendline("{},{}".format(guessx, guessy))
				# Read what happened
				data = comm.readline().strip()
				board = update_board(board, guessx, guessy, data)
				myturn = False
			else:
				# Read opponent's guess
				data = comm.readline()
				myturn = True
		except socket.error:
			# Game is over, we either won or lost
			print "Game Finished"


play_game()

