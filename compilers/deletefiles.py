import os, shutil


from commonpaths import *

#STARTING_GATE_PATH / WORKING_PATH / PLAYER_PATH

#to remove tree shutil.rmtree 


    

def deletefiles(name):

    directoriestoremove = [
        STARTING_GATE_PATH + name,
        WORKING_PATH + name + '_folder',
        PLAYER_PATH + name + '_folder' ]

    filestodelete = [
        WORKING_PATH + name,
        PLAYER_PATH + name ]
        
    for d in directoriestoremove:
        try:
            os.system('rm -r %d' % d)
        except OSError:
            print "failed to remove %s" % d
            
        
    for f in filestodelete:
        try:
            os.system('rm %s' % f)
        except OSError:
            print "failed to remove %s" % f
