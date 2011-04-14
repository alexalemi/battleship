#! /usr/bin/env python


#import argparss
import random, sys

lasthit = ''
lastguess = ''


spotsleft = []
for l in ["A","B","C","D","E","F","G","H","I","J"]:
    for n in range(10):
        spotsleft.append(l+str(n))
        
guessspots = ['A0','A1','A2','A3','A4','B0','B1','B2','B3','C0','C1','C2','D0','D1','D2','E0','E1']

def init():
    global lasthit, lastguess, spotsleft,guessspots
    lasthit = ''
    lastguess = ''

    spotsleft = []
    for l in ["A","B","C","D","E","F","G","H","I","J"]:
        for n in range(10):
            spotsleft.append(l+str(n))
            

    guessspots = ['A0','A1','A2','A3','A4','B0','B1','B2','B3','C0','C1','C2','D0','D1','D2','E0','E1']

def genboard():
    init()
    print "A0D B0D C0D D0D E0D"
    
def makeguess():
    if len(guessspots) > 0:
        guess = guessspots[0]
        guessspots.remove(guess)
        spotsleft.remove(guess)
        
    else:
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
    
    