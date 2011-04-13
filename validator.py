from database.models import *
setup_all()

from compilers import py_comp, c_comp, cpp_comp, octave_comp, perl_comp, java_comp
COMPILER_DICT = {'python':  py_comp , 'c': c_comp , 'c++' : cpp_comp , 'octave': octave_comp , 'perl' : perl_comp , 'java': java_comp }

from scripts.tester import myprogramtester


def validate_script(name, src, helperfile, language, **kwargs):
    #this verifies the code, kwargs are name / src / helperfile



    programdict = {}
    programdict['name'] = name
    programdict['src'] = src
    programdict['helperfile'] = helperfile
    programdict['language'] = language

    p = Program(**programdict)
    session.commit()

    comp = COMPILER_DICT[language]
    print "Attempting to save source"
    comp.savethesource(name,src)
    print "Attempting to move to working directory and compile"""
    comp.movetoworkingandcompile(name,helperfile)
    
    qvalid = True
    print "About to test program"
    try:
        qvalid = myprogramtester(name)

    except IOError:
        qvalid=False
    
    if qvalid:
        comp.moveexecutable(name,helperfile)
        p.valid = True
        session.commit()
    
    print "OUTPUT @@" + str(1*qvalid) + "@@"
