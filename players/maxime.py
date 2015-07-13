#!/usr/bin/env python3
import logging
import random
import socket
import sys
import math


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

    def read_line(self):
        return self.sock.recv(1024).decode('ascii').strip()

    def write_line(self, line):
        self.sock.send(bytes(line + '\n', 'ascii'))


# Helpers

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
        self._board = [[' ' for _ in range(10)] for _ in range(10)]

        # heat map
        self._guess_map = [[0. for _ in range(10)] for _ in range(10)]

        for x in range(10): # increase the heat on the borders
            self._guess_map[0][x] += 1.
            self._guess_map[1][x] += 0.5
            self._guess_map[8][x] += 0.5
            self._guess_map[9][x] += 1.
            self._guess_map[x][0] += 1.
            self._guess_map[x][1] += 0.5
            self._guess_map[x][8] += 0.5
            self._guess_map[x][9] += 1.

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

    def guess(self):
        # get all hits
        hits = set()
        for i in range(10):
            for j in range(10):
                if self._board[i][j] in 'HABSDP':
                    hits.add((i, j))

        while hits:
            hit = hits.pop()
            nearby_hits = list(filter(lambda c: self._board[c[0]][c[1]] in 'HABSDP', adjacent_coordinates(hit)))
            logging.debug('hit: %s nearby_hits: %s' % (repr(hit), repr(nearby_hits)))

            if not nearby_hits:
                # no hit nearby, we shoot!
                min_value = min(self._guess_map[i][j] for i, j in adjacent_coordinates(hit))

                guesses = []
                for i, j in adjacent_coordinates(hit):
                    if abs(self._guess_map[i][j] - min_value) < 1e-6:
                        guesses.append((i, j))

                return random.choice(guesses)
            else:
                # TODO: clean-up
                cluster = {hit}
                nearby_hit = nearby_hits[0]
                direction = nearby_hit[0] - hit[0], nearby_hit[1] - hit[1]

                current = hit
                while valid_coordinate(current) and self._board[current[0]][current[1]] in 'HABSDP':
                    cluster.add(current)
                    current = current[0] + direction[0], current[1] + direction[1]

                if valid_coordinate(current) and self._board[current[0]][current[1]] == ' ':
                    return current

                current = hit
                while valid_coordinate(current) and self._board[current[0]][current[1]] in 'HABSDP':
                    cluster.add(current)
                    current = current[0] - direction[0], current[1] - direction[1]

                if valid_coordinate(current) and self._board[current[0]][current[1]] == ' ':
                    return current

                logging.debug('cluster: %s' % repr(cluster))
                for point in cluster:
                    if point in hits:
                        hits.remove(point)

        # guess using the guess_map
        min_value = min(min(self._guess_map[i]) for i in range(10))

        guesses = []
        for i in range(10):
            for j in range(10):
                if abs(self._guess_map[i][j] - min_value) < 1e-6:
                    guesses.append((i, j))

        # pick a random one
        return random.choice(guesses)

    def result(self, guess, data):
        # update the guess map
        for i, j in nearby_coordinates(guess, 1):
            self._guess_map[i][j] += 2.0 - distance(guess, (i, j))

        # update opponent board
        i, j = guess
        if data[0] == 'S':
            self._board[i][j] = data[1]
        else:
            self._board[i][j] = data

        self._print_board()
        self._print_guess_map()

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
            logging.debug('#' + ''.join(self._board[i]) + '#')
        logging.debug('#' * 12)

    def _print_guess_map(self):
        logging.debug('guess map:')
        logging.debug('#' * 52)
        for i in range(10):
            logging.debug('#' + ''.join(map(lambda x: '%.2f ' % x, self._guess_map[i])) + '#')
        logging.debug('#' * 52)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('missing argument: port')
    else:
        logging.basicConfig(filename='logs/maxime.py', filemode='w', level=logging.DEBUG)
        g = TCPGame(Player(), int(sys.argv[1]))
        g.run()
