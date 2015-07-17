"""
This generates the static website
"""

import jinja2
import os
import logging
from collections import namedtuple

logging.basicConfig(level=logging.DEBUG)

TEMPLATES_PATH = "templates"
STATIC_PATH = "static"

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))


leaderboard_row = namedtuple('row', 'rank name exposure mean sigma wins losses')

def make_index():
    """ Make the index page, which has the leaderboard """
    template = env.get_template("index.html")
    with open("leaderboard.txt","r") as f:
        data = f.readlines()[2:]
    
    leaderboard = [ leaderboard_row(*line.split()) for line in data ]    
    with open(os.path.join(STATIC_PATH, "index.html"), "w") as f:
        f.write(template.render(leaderboard=leaderboard, title="Battleship Leaderboard"))

    

def make_games():
    """ Make the page for each game, as well as the games overview page """

def make_players():
    """ Make the page for all the players, and each player individually """

def make_about():
    """ make the about page """

def make_website():
    logging.debug("making the whole website")
    make_index()
    make_games()
    make_players()
    make_about()


if __name__ == "__main__":
    make_website()
    

