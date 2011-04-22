from database.models import *
setup_all()


def update_some_stats(program1name):
    print "Inside the stats updator"
    #looks like a game has finished, update the stats for the affected players
    
    player1 = Program.query.filter_by(name=program1name).one()
    
    print "Accessing all of the game lists"
    program1asfirstplayer =  player1.firstplayergames
    program1assecondplayer = player1.secondplayergames
    program1winninggames  = player1.winninggames
    program1losinggames = player1.losinggames
    
    
    #update games played
    print "Update the number of games played"
    player1.gamesplayed = len(program1asfirstplayer) + len(program1assecondplayer)
    player1.gameswon = len( program1winninggames ) 
    if player1.gamesplayed:
        player1.winpercentage = player1.gameswon* 1.0/player1.gamesplayed
    
    #update the hitsperguess away and home
    print "Trying to update all of the hitsperguess stats"
    if program1winninggames:
        player1.hitsperguessaway = sum([ 17.0/( ( g.turns + 2 )/2) for g in program1winninggames])/(1.0 * len(program1winninggames) )
    if program1losinggames:
        player1.hitsperguesshome =  sum([g.remaininghealth*1.0/( (g.turns+2)/2) for g in program1losinggames]) /( 1.0 * len(program1losinggames ) )


    print "Saving the players"
    session.commit()



