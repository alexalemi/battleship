
from programplayer import ProgramPlayer

def myprogramtester(name):
    """ Tests a program by loading the program module and seeing if it does its job. """
    qvalid = True
    try:
        prog = ProgramPlayer(name,testing=True)
        print "Player generated"
        
        print "Asking to generate board: "
        board = prog.genboard('testing')
        print "Board Generated"
        
        
        print "Simulating some turns: "
        for i in range(10):
            guess = prog.makeguess()
            status = prog.checkguess(guess)
            prog.recordguess(status)
            
        print "Simulating end message"    
        prog.endgame('W')
        
        print "Generating another board"
        prog.genboard('testing')
        
        print "Testing Kill"
        prog.kill()
    except Exception("FailWhale"):
        qvalid = False
        
    return qvalid
    




