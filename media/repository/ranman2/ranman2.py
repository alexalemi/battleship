#! /usr/bin/env python


#import argparss
import random, sys

lasthit = ''
lastguess = ''


spotsleft = []
for l in ["A","B","C","D","E","F","G","H","I","J"]:
    for n in range(10):
        spotsleft.append(l+str(n))

def init():
    global lasthit, lastguess, spotsleft
    lasthit = ''
    lastguess = ''

    spotsleft = []
    for l in ["A","B","C","D","E","F","G","H","I","J"]:
        for n in range(10):
            spotsleft.append(l+str(n))

def genboard():
    init()
    print "A0D B0D C0D D0D E0D"
    
def makeguess():
    guess = random.choice(spotsleft)

    spotsleft.remove(guess)

    print guess
    
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
            
        elif inp[0] == 'K':
            running = False
    
    print "Program terminated.\n"
    
    