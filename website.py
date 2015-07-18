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

def get_games():
    records = glob.glob(os.path.join(RESULTS_PATH, "*.json"))
    games = []
    for record in records:
        games.append(int(os.path.basename(record).split(".")[0]))
    return games
        
games = get_games()

def collect_errors():
    logging.info("Collecting errored games")
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

errors = collect_errors()

def make_index():
    """ Make the index page, which has the leaderboard """
    logging.info("Making index page")
    template = env.get_template("index.html")
    with open("leaderboard.txt","r") as f:
        data = f.readlines()[2:]
    leaderboard = [ leaderboard_row(*line.split()) for line in data ]    
    with open(os.path.join(STATIC_PATH, "index.html"), "w") as f:
        f.write(template.render(leaderboard=leaderboard, errors=errors, title="Battleship Leaderboard"))

def make_games():
    """ Make the page for each game, as well as the games overview page """
    logging.info("Making game pages")
    template = env.get_template("game.html")
    for game in games:
        logging.info("Making game page for pk=%d", game)
        with open(os.path.join(RESULTS_PATH, "{}.json".format(game))) as f:
            data = json.load(f)
        with open(os.path.join(STATIC_PATH, "{}.html".format(game)), 'w') as f:
            f.write(template.render(pk=game, data=data))

def make_players():
    """ Make the page for all the players, and each player individually """

def make_about():
    """ make the about page """
    logging.info("Making the about page")
    template = env.get_template("about.html")
    with open(os.path.join(STATIC_PATH, "about.html"), "w") as f:
        f.write(template.render(title="About"))

def copy_css():
    logging.info("Copying the css file")
    shutil.copyfile(os.path.join(TEMPLATES_PATH, CUSTOM_CSS),
            os.path.join(STATIC_PATH, CUSTOM_CSS))

def copy_records():
    logging.info("Copying over the records")
    static_records = os.path.join(STATIC_PATH, "records")
    try:
        shutil.rmtree(static_records)
    except OSError:
        pass
    shutil.copytree(RESULTS_PATH, static_records)

def make_website():
    logging.debug("making the whole website")
    make_index()
    make_games()
    make_players()
    make_about()
    copy_css()
    copy_records()


if __name__ == "__main__":
    make_website()
    

