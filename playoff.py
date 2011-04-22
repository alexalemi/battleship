from scripts.gameplayer import launchgames

from database.models import *
setup_all()

from stats import update_some_stats


def playoff(name1,name2,N=100):
    """ This function will play a series of games between two players, it will then save the results of those games in the database """

    #get the results of a bunch of games that have been played
    results, gameinfodict = launchgames(name1,name2,N)
    
    for gameinfo in gameinfodict:
        
        #get the database IDs of the players involved, according to name
        print "Recieved a game <%s> vs <%s> won by <%s> " % ( gameinfo['player1name'], gameinfo['player2name'], gameinfo['winnername'] )
        player1 = Program.query.filter_by(name=gameinfo['player1name']).one()
        player2 = Program.query.filter_by(name=gameinfo['player2name']).one()
        winner = Program.query.filter_by(name=gameinfo['winnername']).one()
        loser = Program.query.filter_by(name=gameinfo['losername']).one()

        #populate the gamedict, this will be passed to the Game Model class to create an entry.
        gamedict = {}
        gamedict['player1'] = player1
        gamedict['player2'] = player2
        gamedict['winner'] = winner
        gamedict['loser'] = loser
        for elem in ['finished','moves','duration','turns','remaininghealth','player1board','player2board','failwhale']:
            gamedict[elem] = gameinfo[elem]

        #create the entry and save the database
        Game(**gamedict)
        session.commit()
        
    update_some_stats(name1)
    update_some_stats(name2)
    from make_website import *

        




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
