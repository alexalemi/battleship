#!/usr/bin/env pypy3
import logging
import random
import socket
import sys
import math
import time


SHIP_LENGTH = {'A': 5, 'B': 4, 'S': 3, 'D': 3, 'P': 2}
ALL_POSITIONS = tuple((i, j) for i in range(10) for j in range(10))
TIMEOUT = 2.0


class Game:
    def __init__(self, player):
        self.player = player

    def run(self):
        turn, opponent = self.read_line().split(',')
        myturn = turn == '0'
        self.player.init(myturn, opponent)

        board = self.player.board()

        for line in board:
            self.write_line(''.join(line))

        # main loop
        while True:
            if myturn:
                guess = self.player.guess()
                self.write_line('%d,%d' % guess)
                data = self.read_line()
                if data == 'W':
                    self.player.win()
                    return
                else:
                    self.player.result(guess, data)
            else:
                data = self.read_line()
                if data == 'L':
                    self.player.lost()
                    return
                else:
                    self.player.opponent_guess(data)

            myturn = not myturn


class PipeGame(Game):
    def read_line(self):
        return input()

    def write_line(self, line):
        print(line)


class TCPGame(Game):
    def __init__(self, player, port):
        super().__init__(player)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', port))
        self.sock_in = self.sock.makefile('r')

    def read_line(self):
        return self.sock_in.readline().strip()

    def write_line(self, line):
        self.sock.send(bytes(line + '\n', 'ascii'))


# Helpers

def point_add(p1, p2):
    return p1[0] + p2[0], p1[1] + p2[1]


def point_sub(p1, p2):
    return p1[0] - p2[0], p1[1] - p2[1]


def point_mul(k, p):
    return k * p[0], k * p[1]


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def valid_coordinate(coord):
    return coord[0] >= 0 and coord[0] <= 9 and coord[1] >= 0 and coord[1] <= 9


def nearby_coordinates(coord, distance):
    i, j = coord
    for x in range(max(0, i - distance), min(9, i + distance) + 1):
        for y in range(max(0, j - distance), min(9, j + distance) + 1):
            yield (x, y)


def adjacent_coordinates(coord):
    i, j = coord
    return filter(valid_coordinate, [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)])


def all_ship_positions(length, condition):
    for i, j in ALL_POSITIONS:
        if all(i + k <= 9 and condition((i + k, j)) for k in range(length)):
            yield set((i + k, j) for k in range(length))

        if all(j + k <= 9 and condition((i, j + k)) for k in range(length)):
            yield set((i, j + k) for k in range(length))


def is_intersection_null(left, right):
    for pos in left:
        if pos in right:
            return False

    return True


class Player:
    def init(self, myturn, opponent):
        logging.info('[init] The game starts!')
        logging.debug('[init] myturn=%s opponent=%s' % (myturn, opponent))

        # status of the opponent board
        # ' ': unknow, 'M': miss, 'H': hit, 'A', 'B', 'S', 'D', 'P': ship
        self._board = {pos: ' ' for pos in ALL_POSITIONS}

        # set of guesses
        self._guesses = set()

        # set of ships still alive
        self._ships = {'A', 'B', 'S', 'D', 'P'}

        # probability map
        self.reset_proba_map()

        # hunting mode settings
        # we only strike if (i + j) % self._parity_mod == self._parity_value
        self._parity_mod = 2
        self._parity_val = random.randint(0, 1)

        # set of (unresolved) hits
        self._hits = set()

    # generate our board
    def board(self):
        board = {pos: '0' for pos in ALL_POSITIONS}

        for ship, length in SHIP_LENGTH.items():
            positions = list(all_ship_positions(length, lambda p: board[p] == '0'))
            points = random.choice(positions)
            for pos in points:
                board[pos] = ship

        return [[board[i, j] for j in range(10)] for i in range(10)]

    def guess(self):
        self._start_time = time.time()
        return self.guess_target_mode() or self.guess_hunting_mode()

    def is_possibly_ship(self, pos):
        if pos in self._guesses:
            return False

        for ship in self._ships:
            length = SHIP_LENGTH[ship]
            positions = all_ship_positions(length, lambda p: (p in self._hits and self._board[p] == 'H') or p not in self._guesses)
            for points in positions:
                if pos in points:
                    return True

        return False

    def guess_target_mode(self):
        if not self._hits:
            return None

        logging.debug('[guess] target mode')

        ships = {self._board[pos]: pos for pos in self._hits if self._board[pos] in 'ABSDP'}
        for ship, ship_pos in ships.items():
            length = SHIP_LENGTH[ship]
            positions = all_ship_positions(length, lambda p: p in self._hits and (self._board[p] == 'H' or self._board[p] == ship))
            positions = [points for points in positions if ship_pos in points]

            assert len(positions) == 1
            logging.debug('[target] sunken ship: %r' % positions[0])

            for pos in positions[0]:
                self._hits.remove(pos)

        if not self._hits:
            return None

        # no sunken ship
        hit = next(iter(self._hits))
        nearby_hits = set(adjacent_coordinates(hit)).intersection(self._hits)
        logging.debug('[target] from hit: %r nearby hits: %r' % (hit, nearby_hits))

        for nearby_hit in nearby_hits:
            # grab all hits on the same line, starting from `hit`
            cluster = {hit, nearby_hit}
            guesses = []
            direction = point_sub(nearby_hit, hit)

            current = point_add(nearby_hit, direction)
            while valid_coordinate(current) and current in self._hits:
                cluster.add(current)
                current = point_add(current, direction)

            if valid_coordinate(current) and current not in self._guesses and self.is_possibly_ship(current):
                guesses.append(current)

            current = point_sub(hit, direction)
            while valid_coordinate(current) and current in self._hits:
                cluster.add(current)
                current = point_sub(current, direction)

            if valid_coordinate(current) and current not in self._guesses and self.is_possibly_ship(current):
                guesses.append(current)

            # found a cluster
            logging.debug('[target] found cluster: %r' % cluster)

            if guesses:
                return self.shoot(guesses)

        # no nearby hits
        logging.debug('[target] no nearby hits, shooting nearby')
        positions = set(adjacent_coordinates(hit)).difference(self._guesses)
        positions = [pos for pos in positions if self.is_possibly_ship(pos)]
        return self.shoot(positions)

    def guess_hunting_mode(self):
        logging.debug('[guess] hunting mode')
        self.reset_proba_map()
        self.fill_proba_map()
        positions = [(i, j) for i, j in ALL_POSITIONS if (i + j) % self._parity_mod == self._parity_val]
        return self.shoot(positions)

    def reset_proba_map(self):
        self._proba_map = {pos: 0 for pos in ALL_POSITIONS}

    def fill_proba_map(self):
        # optimized version of fill_proba_map
        ships_possible_positions = {}
        for ship in self._ships:
            length = SHIP_LENGTH[ship]
            positions = all_ship_positions(length, lambda p: self._board[p] == ' ')
            ships_possible_positions[ship] = list(positions)

        ships_order = list(self._ships)
        ships_order.sort(key=lambda ship: len(ships_possible_positions[ship]), reverse=True)

        iterations = 0
        while iterations < 100000 and time.time() - self._start_time < TIMEOUT - 0.1:
            ships = [] # list of ships (set of positions)
            ships_positions = set() # taken positions

            for ship in ships_order:
                positions = ships_possible_positions[ship]
                if ships: # not the first ship
                    positions = [points for points in positions if is_intersection_null(points, ships_possible_positions)]
                points = random.choice(positions)
                ships.append(points)
                ships_positions.update(points)

            for points in ships:
                for pos in points:
                    self._proba_map[pos] += 1

            iterations += 1

        logging.debug('[fill_proba_map] %d iterations in %s secs' % (iterations, time.time() - self._start_time))

    def generate_random_ships(self):
        ships = [] # list of ships (set of positions)
        ships_positions = set() # taken positions

        for ship in self._ships:
            length = SHIP_LENGTH[ship]
            positions = all_ship_positions(length, lambda p: self._board[p] == ' ' and p not in ships_positions)
            points = random.choice(list(positions))
            ships.append(points)
            ships_positions.update(points)

        return ships

    def shoot(self, positions):
        positions = set(positions).difference(self._guesses)
        return max(positions, key=lambda p: self._proba_map[p])

    def result(self, guess, data):
        # update opponent board
        if data[0] == 'S':
            self._board[guess] = data[1]
        else:
            self._board[guess] = data

        # update the set of guesses
        self._guesses.add(guess)

        # update ships
        if data[0] == 'S':
            self._ships.remove(data[1])

        # update hunting mode settings
        if data[0] == 'S':
            min_length = min(SHIP_LENGTH[ship] for ship in self._ships)
            if min_length > self._parity_mod:
                self._parity_mod = min_length
                self._parity_val = random.randint(0, 1)
                logging.debug('[result] hunting mode settings updated [mod=%d val=%d]' % (self._parity_mod, self._parity_val))

        # update hits
        if data[0] in 'HS':
            self._hits.add(guess)

        # debug
        self._print_board()

    def opponent_guess(self, guess):
        pass

    def win(self):
        logging.info('Win \o/')

    def lost(self):
        logging.info(':(')

    def _print_board(self):
        logging.debug('opponent board:')
        logging.debug('#' * 12)
        for i in range(10):
            logging.debug('#' + ''.join(self._board[i, j] for j in range(10)) + '#')
        logging.debug('#' * 12)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('missing argument: port')
    else:
        logging.basicConfig(filename='logs/maxime.py', filemode='w', level=logging.DEBUG)
        g = TCPGame(Player(), int(sys.argv[1]))
        g.run()
