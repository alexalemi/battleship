
"""
This file creates the database Models I use to save the database as a sqlite3 database using
SQLAlchemy, driven by Elixir to make it django-like

"""



from elixir import *
from datetime import datetime

metadata.bind = "sqlite:///data.db"
#metadata.bind.echo= True


class Program(Entity):
    """ The Program model stores all of the data I need to specify a program,
    including its name, author, description and the like, as well as its statistics 
    """
    name = Field(String(30), unique=True)
    description = Field(String(300), default="")
    author = Field(String(30))
    
    src = Field(Text)
    helperfile = Field(Boolean)
    language = Field(String(30))
    valid = Field(Boolean, default=False)
    failwhale = Field(Boolean)
    failures = Field(Integer)

    timestamp = Field(DateTime, default=datetime.now())
    
    
    rating = Field(Float,default = 1500)
    rd = Field(Float,default = 350)
    ranking = Field(Integer,default=-1)

    
    hitsperguesshome = Field(Float,default = 0)
    hitsperguessaway = Field(Float,default = 0)
    
    gamesplayed = Field(Integer,default = 0)
    gameswon = Field(Integer,default = 0)
    winpercentage = Field(Float,default = 0 )
    
    
    #games = OneToMany('Game')
    firstplayergames = OneToMany('Game',inverse='player1')
    secondplayergames = OneToMany('Game',inverse='player2')
    winninggames = OneToMany('Game',inverse='winner')
    losinggames = OneToMany('Game',inverse='loser')


    def __repr__(self):
        return "Name: <%s> | %s | V: %s" % (self.name, self.language, str(self.valid))
    
class Game(Entity):
    """ This is the Game Model which will store all of the information I need to specify a game """
    player1 = ManyToOne('Program')
    player2 = ManyToOne('Program')
    
    finished = Field(Boolean)
    
    moves = Field(Text)
    
    player1board = Field(String(20))
    player2board = Field(String(20))
    
    winner = ManyToOne('Program')
    loser = ManyToOne('Program')
    
    creation_time = Field(DateTime, default = datetime.now )
    
    played_time = Field(DateTime)
    
    duration = Field(Float)
    
    turns = Field(Integer)
    remaininghealth = Field(Integer)
    
    failwhale = Field(Boolean)

    valid = Field(Boolean,default=True)


    def __repr__(self):
        return "<%s> vs <%s>, won by <%s>" % (self.player1.name,self.player2.name,self.winner.name)
