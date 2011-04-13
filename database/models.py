
from elixir import *
from datetime import datetime

metadata.bind = "sqlite:///data.db"
metadata.bind.echo= True


class Program(Entity):
    name = Field(String(30), unique=True)
    description = Field(String(300), default="")
    src = Field(Text)
    helperfile = Field(Boolean)
    language = Field(String(30))
    valid = Field(Boolean, default=False)
    failwhale = Field(Boolean)
    failures = Field(Integer)
    
    
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
