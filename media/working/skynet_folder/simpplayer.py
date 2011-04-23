from scipy import zeros_like, cumsum

lets = "ABCDEFGHIJ"

from loader import *

def numtocoords(num):
    return lets[num/10] + str(num%10)


guessed = []

infod = {}

shipsleft = [1,2,3,4,5]
hitslist = []

def seeit(mat,*args,**kwargs):
    clf()
    imshow(rot90(flipud(mat.reshape((10,10))),3),interpolation='nearest',*args,**kwargs)


def guess():
    guessmat = zeros_like(B[:,0])

    for s in shipsleft:
        guessmat += B[:,s-1]
    
        for key,val in infod.iteritems():
            if val == -1:
                for ss in shipsleft:
                    guessmat += W[:,s-1,key,ss]
            else:
                guessmat += W[:,s-1,key,val]

    return guessmat


def pointtoguess(guessmat,plotbool=True):
    guessmat[infod.keys()] = 0
    
    maxspot = argmax(guessmat)

    guessmat = guessmat / sum(guessmat)
    if plotbool:
        seeit(guessmat)
    normed = cumsum( guessmat / sum(guessmat) )
    loc = sum(normed < rand() )
    

    return maxspot

def doit():
    global hitslist, indod

    done = False
    while not done:
        b = guess()
        p = pointtoguess(b)
        cord = numtocoords(p)

        print "Next guess is <%d> or <%s>" % (p, cord)
        inp = raw_input("Result>")
        if inp == "q":
            done = True
        else:
            if inp=='-1':
                hitslist.append(p)    
            infod[p] = int(inp)







