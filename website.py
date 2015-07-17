"""
This generates the static website
"""

import jinja2
import os
import logging
import glob
import json
import shutil
from collections import namedtuple, defaultdict

logging.basicConfig(level=logging.DEBUG)

TEMPLATES_PATH = "templates"
STATIC_PATH = "static"
RESULTS_PATH = "records"
CUSTOM_CSS = "custom.css"

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))


leaderboard_row = namedtuple('row', 'rank name exposure mean sigma wins losses')

def collect_errors():
    records = glob.glob(os.path.join(RESULTS_PATH, "*.json")) 
    errors = defaultdict(list)
    for fl in records:
        with open(fl) as f:
            dat = json.load(f)
        if 'error' in dat:
            players = [dat['player0'], dat['player1']]
            winner = dat['winner']
            badguy = players[1-winner]
            errors[badguy].append(dat.get("id"))  # TODO temporary fix since I didn't have ids
    return errors


def make_index():
    """ Make the index page, which has the leaderboard """
    template = env.get_template("index.html")
    with open("leaderboard.txt","r") as f:
        data = f.readlines()[2:]
    leaderboard = [ leaderboard_row(*line.split()) for line in data ]    
    errors = collect_errors()
    with open(os.path.join(STATIC_PATH, "index.html"), "w") as f:
        f.write(template.render(leaderboard=leaderboard, errors=errors, title="Battleship Leaderboard"))

    

def make_games():
    """ Make the page for each game, as well as the games overview page """

def make_players():
    """ Make the page for all the players, and each player individually """

def make_about():
    """ make the about page """

def copy_css():
    shutil.copyfile(os.path.join(TEMPLATES_PATH, CUSTOM_CSS),
            os.path.join(STATIC_PATH, CUSTOM_CSS))

def make_website():
    logging.debug("making the whole website")
    make_index()
    make_games()
    make_players()
    make_about()
    copy_css()


if __name__ == "__main__":
    make_website()
    

