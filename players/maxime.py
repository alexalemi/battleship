#!/usr/bin/env python3
import logging
import random
import socket
import sys
import math


SHIP_LENGTH = {'A': 5, 'B': 4, 'S': 3, 'D': 3, 'P': 2}


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


def nearby_coordinates(coord, distance):
    i, j = coord
    for x in range(max(0, i - distance), min(9, i + distance) + 1):
        for y in range(max(0, j - distance), min(9, j + distance) + 1):
            yield (x, y)


def valid_coordinate(coord):
    return coord[0] >= 0 and coord[0] <= 9 and coord[1] >= 0 and coord[1] <= 9


def adjacent_coordinates(coord):
    i, j = coord
    return filter(valid_coordinate, [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)])


class Player:
    def init(self, myturn, opponent):
        logging.info('The game starts!')
        logging.debug('myturn=%s opponent=%s' % (myturn, opponent))

        # status of the opponent board
        # ' ': unknow, 'M': miss, 'H': hit, 'A', 'B', 'S', 'D', 'P': ship
        self._board = {(i, j): ' ' for i in range(10) for j in range(10)}

        # set of guesses
        self._guesses = set()

        # heat map
        self._guess_map = {(i, j): 0. for i in range(10) for j in range(10)}

        for x in range(10): # increase the heat on the borders
            self._guess_map[1, x] = self._guess_map[8, x] = 2.
            self._guess_map[x, 1] = self._guess_map[x, 8] = 2.
            self._guess_map[0, x] = self._guess_map[9, x] = 4.
            self._guess_map[x, 0] = self._guess_map[x, 9] = 4.

        # set of positions (either all even or all odd)
        parity = random.randint(0, 1)
        self._parity_pos = {(i, j) for i in range(10) for j in range(10) if (i + j) % 2 == parity}

    # generate our board
    def board(self):
        return ['0000000000',
                '00000000PP',
                '00B0000000',
                '00B000A000',
                '00B000ASSS',
                '00BDDDA000',
                '000000A000',
                '000000A000',
                '0000000000',
                '0000000000']

    def shoot(self, positions):
        positions = set(positions).difference(self._guesses)

        #assert positions, 'positions is empty'
        if not positions: # TODO: this is a temporary fix
            positions = self._parity_pos.difference(self._guesses)

        min_value = min(self._guess_map[pos] for pos in positions)
        return random.choice([pos for pos in positions if abs(self._guess_map[pos] - min_value) < 1e-6])

    # find a guess or remove at least one hit from self.hits
    def guess_target(self, hit):
        nearby_hits = set(adjacent_coordinates(hit)).intersection(self.hits)
        logging.debug('* found hit: %s nearby_hits: %s' % (repr(hit), repr(nearby_hits)))

        for nearby_hit in nearby_hits:
            # grab all hits on the same line, starting from `hit`
            cluster = {hit, nearby_hit}
            direction = point_sub(nearby_hit, hit)

            current = point_add(nearby_hit, direction)
            while valid_coordinate(current) and current in self.hits:
                cluster.add(current)
                current = point_add(current, direction)

            if valid_coordinate(current) and self._board[current] == ' ':
                return current

            current = point_sub(hit, direction)
            while valid_coordinate(current) and current in self.hits:
                cluster.add(current)
                current = point_sub(current, direction)

            if valid_coordinate(current) and self._board[current] == ' ':
                return current

            # found a cluster
            logging.debug('** found cluster: %s' % repr(cluster))
            ships = {self._board[pos]: pos for pos in cluster if self._board[pos] in 'ABSDP'}

            if not ships:
                logging.debug('** no ship, looking further')
            else:
                ships_length = sum(SHIP_LENGTH[ship] for ship in ships)
                if ships_length == len(cluster):
                    # that's not exactly true, but whatever...
                    logging.debug('** ships %s destroyed' % repr(ships.keys()))
                    for pos in cluster:
                        self.hits.remove(pos)

                    return None
                else:
                    # there is another ship somewhere
                    logging.debug('*** looking for a hidden ship')
                    positions = set()
                    for ship, pos in ships.items():
                        positions.update(adjacent_coordinates(pos))

                    positions = positions.difference(cluster)
                    hits = positions.intersection(self.hits)

                    if not hits:
                        logging.debug('** all ships are in that line')

                        for ship, sunk_pos in ships.items():
                            possibilities = []
                            ship_length = SHIP_LENGTH[ship]
                            for begin in cluster:
                                points = {begin}
                                current = point_add(begin, direction)
                                while current in self.hits and len(points) < ship_length:
                                    points.add(current)
                                    current = point_add(current, direction)

                                if len(points) == ship_length and sunk_pos in points:
                                    possibilities.append(points)
                                    logging.debug('*** possibility: %s' % repr(points))

                            if len(possibilities) == 1:
                                logging.debug('*** only one possibility: %s' % repr(possibilities))
                                for pos in possibilities[0]:
                                    self.hits.remove(pos)

                                return None

                        # otherwise, shoot randomly
                        positions = set()
                        for pos in cluster:
                            positions.update(adjacent_coordinates(pos))
                        positions = positions.difference(cluster)
                        hits = positions.intersection(self.hits)

                        if not hits:
                            logging.debug('** not found, strike randomly')
                            return self.shoot(positions)
                        else:
                            logging.debug('** looking further in another direction')
                            return self.guess_target(random.choice(list(hits)))
                    else:
                        logging.debug('** looking further in another direction')
                        return self.guess_target(random.choice(list(hits)))

        logging.debug('* either no nearby hits, or no ship in a hit line')
        return self.shoot(adjacent_coordinates(hit))

    def guess(self):
        # get all hits to find a target
        self.hits = set(pos for pos in self._guesses if self._board[pos] in 'HABSDP')

        while self.hits:
            hit = next(iter(self.hits))
            guess = self.guess_target(hit)
            if guess:
                return guess

        # otherwise, guess using the guess_map
        return self.shoot(self._parity_pos)

    def result(self, guess, data):
        self._guesses.add(guess)

        # update the guess map
        for pos in nearby_coordinates(guess, 1):
            self._guess_map[pos] += 2.0 - distance(guess, pos)

        # update opponent board
        if data[0] == 'S':
            self._board[guess] = data[1]
        else:
            self._board[guess] = data

        self._print_board()
        #self._print_guess_map()

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

    def _print_guess_map(self):
        logging.debug('guess map:')
        logging.debug('#' * 52)
        for i in range(10):
            logging.debug('#' + ''.join('%.2f ' % self._guess_map[i, j] for j in range(10)) + '#')
        logging.debug('#' * 52)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('missing argument: port')
    else:
        logging.basicConfig(filename='logs/maxime.py', filemode='w', level=logging.DEBUG)
        g = TCPGame(Player(), int(sys.argv[1]))
        g.run()
