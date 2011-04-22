#xml reader import
import xml.etree.ElementTree as etree

#import my tournament models and hence database stuff
from database.models import *
setup_all()

#import the commonpaths
from commonpaths import *

#other useful imports
from datetime import datetime
import os
import itertools

#tournament specific imports
from validator import validate_script
from playoff import playoff


#get the list of directories in the Starting gate
candidates =  os.listdir(STARTING_GATE_PATH)

#get the list of programs currently in the database
progs = Program.query.all()
# and their names
existing_progs = [q.name for q in progs ]
 

#these are the people not in the database
new_guys = [ c for c in candidates if c not in existing_progs ]

#these are the people in the database
same_guys = [ c for c in candidates if c not in new_guys ]
same_guys_times = [ datetime.fromtimestamp(os.path.getatime(os.path.join(STARTING_GATE_PATH,c))) for c in same_guys ]

#these are the people in the database who have a new timestamp,
#   That is, they have been modified since they were saved
diffs = [ same_guys_times[i] - Program.query.filter_by(name=c).one().timestamp for (i,c) in enumerate(same_guys)]
changed_guys = [ c for (i,c) in enumerate(same_guys) if diffs[i].days >= 0 ]

#the full list of things that need to be updated
updatelist = new_guys + changed_guys

#the list of people who are in the database and have not been changed
oldopponents = [p for p in existing_progs if p not in changed_guys]


#if there are any new folders
if new_guys:
    for prog in new_guys:
        #try to read the information needed from the xml file in the directory
        try:
            tree = etree.parse(os.path.join(STARTING_GATE_PATH,prog,'info.xml'))
            root = tree.getroot()

            infodict = {}
            try:
                infodict['name'] = prog
            except IndexError:
                print "Lacking a name section of the xml file for <%s>" % ( prog )
                raise IOError
            try:
                srcfileloc = os.path.join(STARTING_GATE_PATH,prog,root.findall('src')[0].text.strip())
                infodict['src'] = open(srcfileloc,'r').read()
            except IOError:
                print "reading the src file failed for <%s> " % (prog )
                raise IOError
            try:
                infodict['language'] = root.findall('language')[0].text.strip()
            except IndexError:
                print "language tag for <%s> not specified" % (prog)
                raise IOError
            try:
                infodict['helperfile'] = bool(root.findall('helperfile')[0].text.strip())
                print infodict['helperfile']
            except IndexError:
                infodict['helperfile'] = False
            try:
                infodict['author'] = root.findall('author')[0].text.strip()
            except IndexError:
                print "No author specified for <%s>" % (prog)
            try:
                infodict['description'] = root.findall('description')[0].text.strip()
            except IndexError:
                print "No description found for <%s>" % (prog)
            
            validate_script(**infodict)
        except IOError:
            print "XML File for <%s> doesn't seem to be right" % (prog)

#if there are any guys that have changed
if changed_guys:
    for prog in changed_guys:
        #try to read their xml file
        # NOTE this is copied code, maybe make an xml reader function to use twice instead
        try:
            tree = etree.parse(os.path.join(STARTING_GATE_PATH,prog,'info.xml'))
            root = tree.getroot()

            infodict = {}
            try:
                infodict['name'] = prog
            except IndexError:
                print "Lacking a name section of the xml file for <%s>" % ( prog )
                raise IOError
            try:
                srcfileloc = os.path.join(STARTING_GATE_PATH,prog,root.findall('src')[0].text.strip())
                infodict['src'] = open(srcfileloc,'r').read()
            except IOError:
                print "reading the src file failed for <%s> " % (prog )
                raise IOError
            try:
                infodict['language'] = root.findall('language')[0].text.strip()
            except IndexError:
                print "language tag for <%s> not specified" % (prog)
                raise IOError
            try:
                infodict['helperfile'] = bool(root.findall('helperfile')[0].text.strip())
                print infodict['helperfile']
            except IndexError:
                infodict['helperfile'] = False
            try:
                infodict['author'] = root.findall('author')[0].text.strip()
            except IndexError:
                print "No author specified for <%s>" % (prog)
            try:
                infodict['description'] = root.findall('description')[0].text.strip()
            except IndexError:
                print "No description found for <%s>" % (prog)
            infodict['update'] = True
            validate_script(**infodict)
        except IOError:
            print "XML File for <%s> doesn't seem to be right" % (prog)


from multiprocessing import Pool
gamepool = Pool(5)

#try to find all of the new games to play, and play them.
NUM_GAMES = 100
if updatelist:
    if len(updatelist)>1:
        for (p,q) in itertools.combinations(updatelist,2):
            gamepool.apply_async(playoff,(p,q,NUM_GAMES))
    for p in updatelist:
        for q in oldopponents:
            gamepool.apply_async(playoff,(p,q,NUM_GAMES))
