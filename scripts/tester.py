
from programplayer import ProgramPlayer
from gameplayer import launchgames

def myprogramtester(name):
    """ Tests a program by loading the program module and seeing if it does its job. """
    qvalid = True
    try:
        launchgames(name,name,N=10,testing=True)
    except Exception("FailWhale"):
        qvalid = False
        
    return qvalid
    




