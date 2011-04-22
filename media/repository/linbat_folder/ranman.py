#! /usr/bin/env python


#import argparss
import random, sys

import cPickle as pickle
from scipy import zeros_like

lasthit = ''
lastguess = ''
spotsguessed = []

datfile = open('actual.dat','r')
B = pickle.load(datfile)
W = pickle.load(datfile)

BOARDCORDS = "ABCDEFGHIJ"
LETTONUMS = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'I':8, 'J':9}


def numtocoord(num):
    return BOARDCORDS[num/10] + str(num%10)
    
def coordtonum(coord):
    return 10*LETTONUM[coord[0]] + int(coord[1])
    

def init():
    global lasthit, lastguess, spotsguessed
    lasthit = ''
    lastguess = ''

    spotsguessed = []
    info = {}


def genboard():
    init()
    print "A0D B0D C0D D0D E0D"
    
def makeguess():
    global lastguess, spotsguessed
    
    if not info:
        print numtocoord(45)
        
    else:
        guessmat = zeros_like(B)
        for key,val in info.iteritems():
            guessmat += W[:,key,val]
            
        guessmat[spotsguessed] = 0
        lastguess = argmax(guessmat)
        spotsguessed.append(lastguess)
        print numtocoord(nextguess)
        

def updateinfo(inf):
    pass



def mainloop():
    inp = raw_input('>')
    
    return inp
    
if __name__ == '__main__':
    running = True
    init()
    
    while running:
        inp = mainloop()
        
        if inp[0] == 'N':
            genboard()
            
        elif inp[0] == 'F':
            makeguess()
            
        elif inp[0] == 'H':
            updateinfo('H')
        elif inp[0] == 'M':
            updateinfo('M')
        elif inp[0] == 'S'
            
        elif inp[0] == 'K':
            running = False
    
    print "Program terminated.\n"
    
    
