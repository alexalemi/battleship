#get the Models and database
from database.models import *
setup_all()

from datetime import datetime

#import my compiler functions
from compilers import py_comp, c_comp, cpp_comp, octave_comp, perl_comp, java_comp
COMPILER_DICT = {'python':  py_comp , 'c': c_comp , 'cpp' : cpp_comp , 'octave': octave_comp , 'perl' : perl_comp , 'java': java_comp }

#import the tester script
from scripts.tester import myprogramtester


def validate_script(name, src, helperfile, language, **kwargs):
    #this verifies the cofde, kwargs are name / src / helperfile

    #start to create the program dictionary that will be passed to the Program Model
    programdict = {}
    programdict['name'] = name
    programdict['src'] = src
    programdict['helperfile'] = helperfile
    programdict['language'] = language
    
    if 'description' in kwargs:
        programdict['description'] = kwargs['description']
    if 'author' in kwargs:
        programdict['author'] = kwargs['author']

    #if this is an update, just change the relevant entries of the database
    if 'update' in kwargs:
        p = Program.query.filter_by(name=name).one()
        programdict['timestamp'] = datetime.now()
        p.set(**programdict)

        for g in p.firstplayergames + p.secondplayergames:
            g.valid = False
    else:
        #otherwise just create a new program
        p = Program(**programdict)
    
    #save the database
    session.commit()

    #call the compiler functions according to the language
    comp = COMPILER_DICT[language]
    print "Attempting to save source"
    comp.savethesource(name,src)
    print "Attempting to move to working directory and compile"""
    comp.movetoworkingandcompile(name,helperfile)
    
    qvalid = True
    print "About to test program"
    #try to test the program with the program tester
    try:
        qvalid = myprogramtester(name)

    except IOError:
        qvalid=False
    
    #if they passed the test, mark as valid and continue
    if qvalid:
        comp.moveexecutable(name,helperfile)
        p.valid = True
        session.commit()
    
    print "OUTPUT @@" + str(1*qvalid) + "@@"
