
import os, shutil

from commonpaths import *

def savethesource(name,code):
    if not os.path.isdir(STARTING_GATE_PATH+name):
        os.mkdir(STARTING_GATE_PATH+name)
    f = open(STARTING_GATE_PATH + name + '/' + name + '.c','w')
    f.write(code)
    
    f.close()
    
def movetoworkingandcompile(name,helper=False):
    WORKING_DIR = WORKING_PATH + name + '_folder'
    if not os.path.isdir(WORKING_DIR):
        os.mkdir(WORKING_DIR)
    FROM = STARTING_GATE_PATH + name + '/' + name + '.c'
    TO = WORKING_DIR + '/' + name + '.c'
    shutil.copy( FROM , TO)

    if helper:
        HELPER_FILE = WORKING_DIR + '/' + name + '.txt'
        f = open(HELPER_FILE,'w')
        f.write('')
        f.close()


    SCRIPT_PATH = WORKING_PATH + name

    os.system('gcc %s -o %s' %(TO, SCRIPT_PATH) )    
    os.system('chmod +x %s' % SCRIPT_PATH)



    
def moveexecutable(name,helper=False):
    SCRIPT_PATH = WORKING_PATH + name
    

    os.system('cp %s -r %s_folder %s' %  (SCRIPT_PATH, SCRIPT_PATH, PLAYER_PATH ) )
    


