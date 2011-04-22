from jinja2 import Template
import os

#import model
from database.models import *
setup_all()

from sqlalchemy import desc

#get a list of leading programs
programs = Program.query.order_by(desc(Program.winpercentage)).all()


#BASE WEB PATH
BASE_WEB_PATH = 'web/'


from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('battleship', 'templates'))



#make the index page
template = env.get_template('home.html')
f = open(BASE_WEB_PATH +'index.html','w')
f.write( template.render(programs = programs) )
f.close()

#make the about page
template = env.get_template('about/about.html')
f = open(BASE_WEB_PATH + 'about/index.html','w')
f.write( template.render( ) )
f.close()

#make the programs index page
template = env.get_template('programs/index.html')
f = open(BASE_WEB_PATH +'programs/index.html','w')
f.write(template.render(programs = programs))
f.close()


#make the programs details pages
template = env.get_template('programs/detail.html')
for program in programs:
    f = open(os.path.join(BASE_WEB_PATH,'programs',program.name + '.html'),'w')
    f.write(template.render(program=program))
    f.close()


#get all of the games
games = Game.query.all()

"""
#make the games index page
template = env.get_template('games/games.html')
f = open(BASE_WEB_PATH + 'games/index.html','w')
f.write(template.render(games=games))
f.close()
"""


#make the games index page
#group all of the games by pair off
extra = []
for g in games:
    entry = {}
    pair = [g.player1.name, g.player2.name]
    pair.sort()
    entry['pair'] = pair
    entry['A'] = pair[0]
    entry['B'] = pair[1]
    entry['firstplayer'] = g.player1.name
    entry['game'] = g
    extra.append(entry)


template = env.get_template('games/games2.html')
f = open(BASE_WEB_PATH + 'games/index.html','w')
f.write(template.render(extra = extra))
f.close()


#make game detail pages
template = env.get_template('games/gamesdetail.html')
for game in games:
    f = open(BASE_WEB_PATH +'games/' + str(game.id) + '.html','w')
    f.write(template.render(game=game))
    f.close()


