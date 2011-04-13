from scripts.gameplayer import launchgames

from database.models import *
setup_all()


def playoff(name1,name2):
    results, gameinfodict = launchgames(name1,name2)
    
    for gameinfo in gameinfodict:
        
        print "Recieved a game <%s> vs <%s> won by <%s> " % ( gameinfo['player1name'], gameinfo['player2name'], gameinfo['winnername'] )
        player1 = Program.query.filter_by(name=gameinfo['player1name']).one()
        player2 = Program.query.filter_by(name=gameinfo['player2name']).one()
        winner = Program.query.filter_by(name=gameinfo['winnername']).one()
        loser = Program.query.filter_by(name=gameinfo['losername']).one()

        gamedict = {}
        gamedict['player1'] = player1
        gamedict['player2'] = player2
        gamedict['winner'] = winner
        gamedict['loser'] = loser
        for elem in ['finished','moves','duration','turns','remaininghealth','player1board','player2board','failwhale']:
            gamedict[elem] = gameinfo[elem]

        Game(**gamedict)
        session.commit()

        




""" For informational purposes, this is what gets put in the dict

            self.info['player1name'] = self.playernames[self.firstplayer]
            self.info['player2name'] = self.playernames[1*(self.firstplayer==0)]
            self.info['finished'] = True
            self.info['moves']= self.moves
            self.info['winnername'] = self.playernames[winner]
            self.info['losername'] = self.playernames[1*(winner==0)]
            self.info['duration'] = self.time
            self.info['turns'] = self.turn
            self.info['remaininghealth'] = self.remaininghealth
            self.info['player1board'] = self.player1.boardstring
            self.info['player2board'] = self.player2.boardstring
            self.info['failwhale'] = False

"""


""" Also, this is in the model for Game

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

"""
