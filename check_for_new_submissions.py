import xml.etree.ElementTree as etree

from database.models import *
setup_all()

from commonpaths import *

from datetime import datetime

import os

from validator import validate_script

from playoff import playoff

import itertools

candidates =  os.listdir(STARTING_GATE_PATH)


progs = Program.query.all()
existing_progs = [q.name for q in progs ]
 

new_guys = [ c for c in candidates if c not in existing_progs ]

same_guys = [ c for c in candidates if c not in new_guys ]
same_guys_times = [ datetime.fromtimestamp(os.path.getatime(os.path.join(STARTING_GATE_PATH,c))) for c in same_guys ]

diffs = [ same_guys_times[i] - Program.query.filter_by(name=c).one().timestamp for (i,c) in enumerate(same_guys)]
changed_guys = [ c for (i,c) in enumerate(same_guys) if diffs[i].days >= 0 ]

updatelist = new_guys + changed_guys

oldopponents = [p for p in existing_progs if p not in changed_guys]


if new_guys:
    for prog in new_guys:
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

if changed_guys:
    for prog in changed_guys:
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


NUM_GAMES = 10
if updatelist:
    if len(updatelist)>1:
        for (p,q) in itertools.combinations(updatelist,2):
            playoff(p,q,N=NUM_GAMES)
    for p in updatelist:
        for q in oldopponents:
            playoff(p,q,N=NUM_GAMES)
