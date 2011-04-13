
import os, shutil


from commonpaths import *

def savethesource(name,code):
    if not os.path.isdir(STARTING_GATE_PATH+name):
        os.mkdir(STARTING_GATE_PATH+name)
    f = open(STARTING_GATE_PATH + name + '/' + name + '.py','w')
    f.write(code)
    
    f.close()
    
    
def movetoworkingandcompile(name,helper=False):
    WORKING_DIR = WORKING_PATH + name + '_folder'
    if not os.path.isdir(WORKING_DIR):
        os.mkdir(WORKING_DIR)
    FROM = STARTING_GATE_PATH + name + '/' + name + '.py'
    TO = WORKING_DIR + '/' + name + '.py'
    shutil.copy( FROM , TO)

    if helper:
        HELPER_FILE = WORKING_DIR + '/' + name + '.txt'
        f = open(HELPER_FILE,'w')
        f.write('')
        f.close()


    SCRIPT_PATH = WORKING_PATH + name
    f = open(SCRIPT_PATH,'w')
    f.write(r"""#! /bin/bash
python %s/%s.py""" % (SCRIPT_PATH + '_folder',name))
    f.close()
    
    os.system('chmod +x %s' % SCRIPT_PATH)

def moveexecutable(name,helper=False):
    SCRIPT_PATH = WORKING_PATH + name
    

    os.system('cp %s -r %s_folder %s' %  (SCRIPT_PATH, SCRIPT_PATH, PLAYER_PATH ) )

    SCRIPT_PATH = PLAYER_PATH + name
    f = open(SCRIPT_PATH,'w')
    f.write(r"""#! /bin/bash
python %s/%s.py""" % (SCRIPT_PATH + '_folder',name))
    f.close()
    
    os.system('chmod +x %s' % SCRIPT_PATH)
    


