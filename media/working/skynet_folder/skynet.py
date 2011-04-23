#! /usr/bin/env python


""" Things to do:

    work out the sink state.
    add in the hit filter
    add in the opp data filter

"""

import cPickle as pickle

from scipy import *
import pylab as py

import scipy as sp
import random
import os

PATH = os.path.split(__file__)[0]


class Skynet:
    def __init__(self):
        
        #load the tensors we use        
        fi = open(os.path.join(PATH,'actual.dat'),'r')
        self.B = pickle.load(fi)
        self.W = pickle.load(fi)
        fi.close()
        
        #the full distro
        self.b = sp.sum(self.B,1)
        
        #define some useful things
        self.board_lengths = [5,4,3,3,2]
        self.ship_nums= [1,2,3,4,5]
        self.ship_indices = [0,0,4,3,2,1]
        self.ship_lengths = {'C':5, 'B':4, 'D':3, 'S':3, 'P':2}
        self.ship_ind_dict = {'C':1, 'B':2, 'D':3, 'S':4, 'P':5}
        #define the letter-number number-letter dictionary
        self.letdict = { 'A':0, 'B':1, 'C':2,
                             'D':3, 'E':4, 'F':5,
                             'G':6, 'H':7, 'I':8, 'J':9,
                             0:'A', 1:'B', 2:'C', 3:'D',
                             4:'E', 5:'F', 6:'G', 7:'H',
                             8:'I', 9:'J'}

        #keep track of the ships we are searching for
        self.shipsleft = [1,2,3,4,5]
        #keep track of registered hits
        self.hitslist = []
        #keep track fo the guesses we've made
        self.guessed = []
        #keep track of our state
        self.state = 0   # 0:FREE / 1:HIT / 2:LOCK
        #dictionary of information we've collected
        self.infod = {}
        #keep track of the last hit
        self.lasthit = -1
        #lock variable
        self.lock = None
        
        
        #track opponent stuff
        self.opponent = ''
        fu = open(os.path.join(PATH,'oppdata.dat'),'r')
        self.opponentdata = pickle.load(fu)
        fu.close()
        
        #initialize the opponent specific data
        self.opphitlist = zeros((100,2),dtype='int')
        self.oppguesslist = zeros(100,dtype='float')
        self.oppnumgames = 0
        self.oppwins = 0
        self.opplosses = 0
        
        #load the boards to choose from
        fo = open(os.path.join(PATH,'board.dat'),'r')
        self.totboards = pickle.load(fo)
        fo.close()
        
    def reinit(self):
        """ reset the initialization stuff """
        #keep track of the ships we are searching for
        self.shipsleft = [1,2,3,4,5]
        #keep track of registered hits
        self.hitslist = []
        #keep track fo the guesses we've made
        self.guessed = []
        #keep track of our state
        self.state = 0
        #dictionary of information we've collected
        self.infod = {}
        #keep track of the last hit
        self.lasthit = -1
        #lock variable
        self.lock = None
        
    def load_opponent_data(self,opponent):
        #load the opponent data
        self.opponent = opponent
        if opponent in self.opponentdata:
            (self.opphitlist,
                self.oppguesslist,
                self.oppnumgames,
                self.oppwins,
                self.opplosses) = self.opponentdata[opponent]
    def save_opponent_data(self):
        """ Save the accumulated opponent data """
        self.opponentdata[self.opponent] = ( self.opphitlist, 
                                                self.oppguesslist,
                                                self.oppnumgames,
                                                self.oppwins,
                                                self.opplosses)
        fu = open('oppdata.dat','w')
        pickle.dump(self.opponentdata,fu)
        fu.close()
        
        
    def wilson2(self,up,down,p,z=1.96):
        """ Function for computing our confidence in spots """
        n = up + down + 0.0000000000001
        q = 1-p

        p = up*q/(up*q + down*p + 0.0000000000001)
        return ( p + 1.0/(2.0*n) * z**2) /(1+ 1.0/n * z**2)
        
    def adder(self,u,v):
        """ function for adding two probability densities """
        return 1.0/(1.0 + ((u-1)/u)*((v-1)/v))

    def viewer(self,mat,*args,**kwargs):
        """ a simple helper function to view a matrix """
        py.imshow(mat.reshape((10,10)), 
            interpolation='nearest',
             *args, **kwargs )
             
    def seeit(self,mat,interpolation='nearest',*args,**kwargs):
        """ Another viewer, but with the correct orientation """
        py.clf()
        py.imshow(rot90(flipud(mat.reshape((10,10))),3),interpolation=interpolation,*args,**kwargs)


    def numtocoords(self,num):
        """ Given a number between 0-99, give the coords """
        return self.letdict[num/10] + str(num%10)

    def coordstonum(self,coords):
        """ Given letter coordinates, return a number between 0-99 """
        return self.letdict[coords[0]] * 10 + int(num%10)

    def gen_random_board(self):
        """ Generate a random board """
        chars = list('ABCDEFGHIJ')
        
        board = []
        for i in self.board_lengths:
            bit = random.randint(0,1)
            if bit:
                x = random.randint(0,9)
                y = random.randint(0,9-i+1)
            else:
                x = random.randint(0,9-i+1)
                y = random.randint(0,9)

            board.append( ((x,y), bit) )
            
        return board
        
    def board_to_string(self,board):
        """ take the boards generated by the random board thing
            and return a valid string """
        outstring = ""
        for entry in board:
            num = entry[0][0]*10 + entry[0][1]
            coord = self.numtocoords(num)
            outstring += coord
            if entry[1] == 0:
                outstring += 'R '
            else:
                outstring += 'D '
        return outstring[:-1]
        
    def good_board(self):
        """ Generate random boards until one of them is valid """
        done = False
        
        while not done:
            done, board, original_board = self.check_board(self.gen_random_board())
        board[board>0] = 1
        return board.flatten(), original_board
        
    def check_board(self, board):
        """ Check the validity of a board """
        checked_board = zeros((10,10),dtype='int')  
        final_board = zeros((10,10),dtype='int')
        
        for (pos,bit),l in zip(board,self.board_lengths):
            if bit:
                checked_board[pos[0],pos[1]:pos[1]+l] += 1
            else:
                checked_board[pos[0]:pos[0]+l, pos[1]] += 1
                
        for (pos,bit),l,ind in zip(board,self.board_lengths,self.ship_nums):
            if bit:
                final_board[pos[0],pos[1]:pos[1]+l] += ind
            else:
                final_board[pos[0]:pos[0]+l, pos[1]] += ind
                    
        if ( sum(checked_board) == sum(self.board_lengths) ) and (checked_board < 2).all() :
            #extra condition
            #if (checked_board[4,4] == 1) and (checked_board[4,5] == 1):
            #    result = True
            #print checked_board
            #else:
            #    result = False
	    result = True
        else:
            result = False
            #print checked_board
        original_board = self.board_to_string(board)
        
        return result, final_board, original_board 

    def hitfilter(self):
        filt = zeros(100,dtype='int')
        
        for hit in self.hitslist:
            if hit + 10 < 100:
                filt[hit+10] = 1
            if hit - 10 >= 0:
                filt[hit-10] = 1
            if hit%10 > 0:
                filt[hit-1] = 1
            if hit%10 < 9:
                filt[hit+1] =1 
        
        #if we have a lock
        if (self.state == 2) and (self.lock is not None):
            #we are in the ones place
            if str(self.lock).isdigit():
                for i in range(100):
                    if i%10 != self.lock:
                        filt[i] = 0
            #we are in row case
            else:
                row = self.letdict[self.lock]
                for i in range(100):
                    if i/10 != self.lock:
                        filt[i] = 0
                        
                
        
        return filt
    
    def guesser(self):
        #make a guess matrix from our information

        #start with zeros
        guessmat = zeros_like(self.B[:,0])
        #for each of the ships we are looking for
        for s in self.shipsleft:
            #add in its base probability
            guessmat += self.B[:,s-1]
        
            #for every piece of information we have
            for key,val in self.infod.iteritems():
                # if it is an unregistered hit
                if val == -1:
                    # assume its a superposition of all available ships
                    for ss in self.shipsleft:
                        # and add in the information
                        guessmat += self.W[:,s-1,key,ss]
                else:
                    #otherwise use the exact information
                    guessmat += self.W[:,s-1,key,val]
                    
        # zero out all of the spots we have already guessed
        guessmat[self.infod.keys()] = 0
        
        if self.state > 0:
            guessmat *= self.hitfilter()
        
        # here is where I should apply other filters I have, either my 
        #       sum on top stuff, or the fixer
        
        return guessmat
        
        
    def pointtoguess(self,guessmat,plotbool=False):
        """ Given a matrix of probabilities, pick at random """
        
        #normalize the matrix
        guessmat = guessmat / sum(guessmat)
        if plotbool:
            self.seeit(guessmat)
        #do a cumulative sum
        normed = cumsum( guessmat  )
        #get the index of the guess
        loc = sum(normed < rand() )
        
        return loc
        
    def recordguess(self,result):
        #make note of the last guess
        if result[0] == 'H':
            #we scored a hit, but don't know what it is
            self.infod[self.lasthit] = -1
            #track opp stats
            self.opphitlist[self.lasthit,0] += 1
            #add to hitslist
            self.hitslist.append(self.lasthit)
            if self.state == 0:
                #if we are FREE goto HIT
                self.state = 1
            elif self.state == 1:
                #if we are HIT goto LOCK
                self.state = 2
                secondtolasthit = self.hitslist[-2]
                if secondtolasthit%10 == self.lasthit%10:
                    #this is the digit case
                    self.lock = secondtolasthit%10
                elif secondtolasthit/10 == self.lasthit/10:
                    self.lock = self.letdict[secondtolasthit/10]
                else:
                    #apparently we didn't find the lock, drop to hit
                    self.state = 1
        elif result[0] == 'M':
            #we missed
            self.infod[self.lasthit] = 0
            #track opp stats
            self.opphitlist[self.lasthit,1] += 1
            if self.state == 2:
                #we missed in LOCK goto HIT
                self.state = 1
                self.lock = None
        elif result[0] == 'S':
            #don't know what to do about sunk ships.
            shipsunk = result[2]
            #track opp stats
            self.opphitlist[self.lasthit,0] += 1
            self.shipsleft.remove(self.ship_ind_dict[shipsunk])
            #we need to find which hits correspond to a ship
            #try the simple thing, assuming we have just sunk a ship.
            
            #add this last guess as a hit
            self.hitslist.append(self.lasthit)            
            if len(self.hitslist) == self.ship_lengths[shipsunk]:
                for hit in self.hitslist:
                    #set the info to be good
                    self.infod[hit] = self.ship_ind_dict[shipsunk]
                # take out the hits
                self.hitslist = []
                # drop back to free
                self.state = 0
            else:
                #print "we have a more complicated hit thing going on"
                #for now, drop down to HIT
                self.state = 0
                
            
            
        
    def noteopponentguess(self,guess):
        #take note of what the opponent did
        pass
        
    def genboard(self,opponent):
        #reinitialize 
        self.reinit()
        
        #load the player information
        self.load_opponent_data(opponent) 
        
        #create a board
        scores = array([ sp.sum(board*self.b) + 0.1*randn() for board,op in self.totboards])
        
        boardtopick = scores.argmin()
        
        #print the board
        print self.totboards[boardtopick][1]
        
        return self.totboards[boardtopick][0]
        
        
        
    def makeaguess(self,testing=False):
        #return our guess
        
        #if self.state == 0:
            #we are FREE, just do it
        loc = self.pointtoguess(self.guesser(),testing)
        self.lasthit = loc
        self.guessed.append(loc)
        print self.numtocoords(loc)
        
        """
        elif self.state == 1:
            #we are in HIT, apply the neighbor filter
            loc = self.pointtoguess(self.guesser(),testing)
            self.lasthit = loc
            self.guessed.append(loc)
        elif self.state == 2:
            #we are LOCK, apply the edge filter
            loc = self.pointtoguess(self.guesser()
        """
        
        return loc

    def shutdown(self):
        #we're done here, save the information we've gathered.
        pass


# Setup the stuff to handle the interaction loop.    
def mainloop():
    inp = raw_input('>')
    return inp
    
if __name__ == '__main__':
    Q = Skynet()
    
    running = True
        
    while running:
        inp = mainloop()
        
        if inp[0] == 'N':
            Q.genboard(inp[2:])
            
        elif inp[0] == 'F':
            Q.makeaguess()
        
        # take in information 
        elif inp[0] == 'H':
            Q.recordguess(inp)
        elif inp[0] == 'M':
            Q.recordguess(inp)
        elif inp[0] == 'S':
            Q.recordguess(inp)
            
            
        elif inp[0] == 'O':
            Q.noteopponentguess(inp)
        
        elif inp[0] == 'K':
            Q.shutdown()
            running = False
    
    print "Program terminated.\n"
    
    
