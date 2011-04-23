from __future__ import division

from scipy import sqrt

def wilson(up,down,z = 1.96):
    n = up + down
    p = up*1.0/n

    return ( p + 1.0/(2.0*n) * z**2  )/(1 + 1.0/n * z**2)

def wilson2(up,down,p,z=1.96):
    n = up + down + 0.0000000000001
    q = 1-p

    p = up*q/(up*q + down*p + 0.0000000000001)
    return ( p + 1.0/(2.0*n) * z**2) /(1+ 1.0/n * z**2)

    




#I need to replace the wilson thing with something that looks for deviations from the expected probabilities from B, and depends on the number of guesses.



#this is the function to add probabilities
def adder(u,v):
    return 1.0/(1.0 + ((u-1)/u)*((v-1)/v))


