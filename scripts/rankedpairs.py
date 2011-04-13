#!/usr/bin/env python

"""
Ranked Pairs Vote Resolver

Written by Andrew Plotkin (erkyrath@eblong.com). This program
is in the public domain.

This is an implementation of the Condorcet Ranked-Pairs system.
See <http://condorcet.org/rp/index.shtml>.

This is not a *perfect* Condorcet implementation. I've made one
modification to the system, added one hack, and left one bug. Sorry!
They were all for pragmatic reasons. I will describe them all further
down.

To use this, create a vote file in the following format:

-----------------------
  * AAA BBB CCC DDD
  # The first line should begin with a *. This defines the list of
  # candidates in the contest. (All on one line, separated by whitespace.)

  # The remaining lines define ballots -- one line per voter.
  
  DDD CCC BBB AAA
  # This is a complete ballot. The voter ranked all four candidates,
  # from DDD (best) to AAA (worst).

  DDD AAA BBB
  # This is an incomplete ballot. The voter only ranked three candidates;
  # he didn't have any opinion about CCC at all. (This neither helps nor
  # hurts CCC.)

  DDD AAA/CCC BBB
  # This ballot contains a tie. The voter liked DDD best, BBB least,
  # and AAA and CCC tied for middle place. This is not the same as the
  # previous ballot, because the voter *did* express opinions about CCC;
  # he says CCC is better than BBB and worse than DDD.

  CCC AAA/DDD/BBB
  # This voter likes CCC best, but sees the other candidates as all
  # equally bad. This ballot *does* hurt AAA, BBB, and DDD.

  AAA
  # This voter says AAA is... well, he isn't saying anything about AAA.
  # This is legal, but pointless. It doesn't express any preferences
  # at all, so it's the same as not voting.

  AAA/DDD
  # This voter ranked AAA and DDD as equal and ignores the others. This
  # is also pointless; it doesn't favor any candidate over another.
-----------------------

To run the script:

  python rpvote.py VOTEFILE

Alternatively, you can use the --complete option:

  python rpvote.py --complete VOTEFILE

With --complete, any incomplete ballot is assumed to have all the missing
candidates tied for last place. In other words, "AAA" is interpreted as
"AAA BBB/CCC/DDD". Use this option if you know that every voter has
seen every candidate.

When you run the script, you will see two charts and a final tally.

The first chart looks like this:

-----------------------
Margins:
    AAA BBB CCC DDD
AAA   `   1  -2  -3
BBB  -1   `  -3  -3
CCC   2   3   `  -1
DDD   3   3   1   `
-----------------------

For any two candidates, this lists the margin between the people who
preferred one and the people who preferred the other. In our example,
two voters preferred AAA over BBB, and one preferred the reverse; the
difference is 1. So AAA's margin over BBB is 1. (And BBB's margin over
AAA is -1.) The margin of DDD over AAA is 3, because three voters
preferred DDD over AAA (and none the reverse).

Ties might appear as 0, or (if nobody expressed a preference at all) a
blank entry.

The second chart:

-----------------------
Outrankings:
    AAA BBB CCC DDD
AAA   `   +   -   -
BBB   -   `   -   -
CCC   +   +   `   -
DDD   +   +   +   `
-----------------------

This expresses which candidates beat which others, once everything is
worked out. In our example, AAA beats BBB, but loses to CCC and to
DDD.

-----------------------
Place: Name (wins, losses, unresolved)
  1: DDD (3, 0, 0)
  2: CCC (2, 1, 0)
  3: AAA (1, 2, 0)
  4: BBB (0, 3, 0)
-----------------------

This is the final tally. Each entry simply reads off a row of the
previous chart; CCC scored two wins (+) and one loss (-), so its
standing is 2, 1, and 0.

The tally is sorted in order of the final standing. Ties will show up
as a " mark in the first column. This code includes a tiebreaker rule
-- see below -- but there can still be genuine ties. For example,
if nobody votes at all, you'd see this tally:

-----------------------
Place: Name (wins, losses, unresolved)
  1: AAA (0, 0, 3)
  ": BBB (0, 0, 3)
  ": CCC (0, 0, 3)
  ": DDD (0, 0, 3)
-----------------------

This indicates that all four candidates were tied for the first (and
only) place.

-----------------------
The caveats:

My modification to Condorcet is to accept incomplete ballots. (All the
sample ballots above which list fewer than four candidates are
incomplete.) An ideal Condorcet system only accepts complete ballots.
If you want to run the election this way, simply reject all incomplete
ballots.

Alternatively, you can add missing entries as a tie for last place.
(The --complete option does this automatically.) So if a voter offers
you "AAA BBB", you would record it as "AAA BBB CCC/DDD". If you do this,
be sure to explain that an incomplete ballot *does* hurt the missing
candidates!

My hack is a tiebreaker rule. An election with few voters will tend
to produce ties. That is, a pair of candidates will be indeterminate --
neither beats the other according to the Condorcet rules. I resolve
these in favor of whichever candidate beat the most other candidates
overall. If that doesn't help, I pick whichever candidate lost to the
fewest others overall.

The bug is in a particular corner case: when a set of pairs have the
same margin, are not contradicted by higher-margin pairs, but
contradict each other. My code tries to resolve this, but not in a
very smart way.
"""

import sys

class Contest:
    """Contest: Represents one contest, with all its candidates and ballots.

    Contest(list) -- constructor

    You create the Contest by passing in a list of candidates (represented
    as short strings.) Then call addballots(), once for each ballot.

    Internal fields:

    entries -- list of entries
    count -- number of entries
    keydict -- dict of entries (for faster lookup)

    colwidth -- maximum length of an entry's name (an integer). This
        is convenient for printing tables.

    ballots -- the list of ballots. (See addballots() for the format.)
    margins -- the margins table

    The margins table is a dict mapping (row,col) tuples to integers.
    Note that margins[(row,col)] = -margins[(col,row)]. Also note that
    this is filled in lazily. If no ballot has compared row to col, then
    (row,col) will not be in the mapping.
    """

    def __init__(self, ents):
        self.entries = ents
        self.count = len(ents)
        self.colwidth = max([ len(key) for key in ents ])
        self.colwidth = max(self.colwidth, 3)
        self.keydict = {}
        for key in ents:
            self.keydict[key] = True
        self.ballots = []
        self.margins = {}

    def iskey(self, key):
        """iskey(key) -> bool

        Is the given key one of the candidates in this contest?
        """
        return self.keydict.has_key(key)

    def addballot(self, ls):
        """addballot(list of lists) -> None

        Adds one ballot to the contest. A ballot is a list of ranks;
        each rank is a list of candidate keys.

        Example: if the voter ranks AA first, BB and CC tied for second,
        and DD third ("AA BB/CC DD") then you should call

        contest.addballot([['AA'], ['BB','CC'], ['DD']])

        Ballots need not be complete. All entries in the ballot must be
        valid contest entries, and there must be no duplicates. (This
        method does no consistency checking.)
        """
        self.ballots.append(ls)

    def printballots(self):
        """printballots() -> None

        Print out the list of ballots in the contest.
        """

        print len(self.ballots), 'ballots:'
        for ballot in self.ballots:
            for ls in ballot:
                if (len(ls) == 1):
                    print ls[0],
                else:
                    print '(' + '/'.join(ls) + ')',
            print
        print

    def computemargins(self):
        """computemargins() -> None

        Once all the ballots are added, call computemargins() to
        create the margins table.

        This just compares every pair of entries in the ballot list,
        and calls applymargin() if they're not in the same rank (i.e., 
        tied). It hits every pair twice -- once in each direction --
        as required by applymargin().
        """

        for ballot in self.ballots:
            ranks = len(ballot)
            for ix in range(ranks):
                for row in ballot[ix]:
                    for jx in range(ranks):
                        if (jx == ix):
                            continue
                        for col in ballot[jx]:
                            self.applymargin(row, col, (ix<jx))

    def applymargin(self, row, col, rowwins):
        """applymargin(row, col, rowwins) -> None

        Internal function used by computemargins(). This adds one to
        the margins table, representing the fact that row beat or lost
        to col.

        Note: this updates the (row,col) entry, but *not* the (col,row)
        entry. You must always call this method twice per pair.
        """

        val = self.margins.get( (row,col), 0)
        if (rowwins):
            val += 1
        else:
            val -= 1
        self.margins[(row,col)] = val

    def printmargins(self):
        """printmargins() -> None

        Print out the margins table.
        """

        print 'Margins:'
        wid = self.colwidth

        print ''.rjust(wid),
        for col in self.entries:
            print col.rjust(wid),
        print

        for row in self.entries:
            print row.rjust(wid),
            for col in self.entries:
                if (col == row):
                    val = '`'
                else:
                    val = self.margins.get((row,col), '')
                print str(val).rjust(wid),
            print
        print

    def compute(self):
        """compute() -> Outcome

        Once you've added the ballots and computed the margins, call
        compute() to work out the final result of the contest. This
        does all the hard work.

        Internal logic: First, we gather up all the margins in the
        margins table, and sort them by how big the margin is. (We only
        look at the positive margins. Remember, negative margins are just
        the same information, backwards.)

        We create a blank Outcome. Then we go through all the pairs, from 
        largest margin to smallest, and add them to the outcome. (Pairs
        that contradict the outcome-so-far are discarded, because they
        have a smaller margin than what's in the outcome. That's the point
        of sorting from largest to smallest.)

        When everything is added, we're done.

        The tricky case is when we have to add several facts at once
        (because they have the same margin), but they contradict each
        other. Which ones do we discard? "All of them" is one possible
        answer, but it's very wasteful. (It winds up discarding facts
        that don't contradict anything, but were just in the wrong place
        at the wrong time.)

        I have a rather hacky solution, which is less wasteful, but
        is still approximate. We have N facts. Make N attempts at adding
        them, each time *skipping* one fact. If the attempt succeeds
        (causes no contradiction), then the fact we skipped must be
        part of the *original* contradiction, so discard it! The hope is
        to retain all the facts that *weren't* part of the original 
        contradiction.

        I think the right answer is: treat the outcome as a directed
        acyclic graph. Add all the facts; then look for loops, and delete
        any newly-added facts that are part of a loop. However, I don't
        feel like implementing that.
        """

        # Gather up and sort the margins.

        dic = {}
        for tup in self.margins.keys():
            val = self.margins.get(tup, 0)
            if (val <= 0):
                continue
            ls = dic.get(val)
            if (not ls):
                dic[val] = [tup]
            else:
                ls.append(tup)

        # Create a blank Outcome.
        outcome = Outcome(self)

        if (not dic):
            # No information at all! Return the blank Outcome.
            return outcome
            
        # Determine the largest margin.
        maxmargin = max([ val for val in dic.keys() ])

        for level in range(maxmargin, 0, -1):
            # Get the list of facts at this margin level.
            ls = dic.get(level)
            if (not ls):
                continue
        
            # Discard any facts that contradict the outcome so far.
            compatls = [ tup for tup in ls if outcome.compatible(*tup) ]

            # Try adding all those facts.
            try:
                newout = outcome.clone()
                for tup in compatls:
                    newout.accept(*tup)
                # Success! Continue with the next margin level.
                outcome = newout
                continue
            except:
                #print 'WARNING: Contradiction at level', level, '('+str(len(compatls)), 'pairs)'
                pass

            # Adding those facts resulted in a contradiction (even though
            # no single fact in the set contradicts the model). We must
            # go through the (hacky) algorithm to decide which facts to
            # discard.

            notguilty = []
            
            for avoid in compatls:
                try:
                    newout = outcome.clone()
                    for tup in compatls:
                        if (tup == avoid):
                            continue
                        newout.accept(*tup)
                except:
                    notguilty.append(avoid)

            if (len(notguilty) == 0 or len(notguilty) == len(compatls)):
                # If we eliminated all the facts, give up. If we 
                # eliminated *no* facts, also give up.
                #print '...all pairs eliminated.'
                continue

            #print '...', len(notguilty), ' pairs remain.'

            # Once again, try adding all the remaining facts.

            try:
                newout = outcome.clone()
                for tup in notguilty:
                    newout.accept(*tup)
                outcome = newout
                continue
            except:
                #print 'WARNING: Contradiction at level', level, 'still exists'
                pass

        return outcome

class Outcome:
    """Outcome: Represents the outcome of a Contest.

    This is generated by the compute() method of Contest. Actually,
    working out a contest generates lots of Outcome objects, but
    only the final one is returned.

    Outcome(Contest) -- constructor

    To create an Outcome, you must pass in the Contest that it will apply
    to. 

    Logically, an Outcome represents an outranking table. For any pair
    of candidates (row, col), the Outcome tells you whether row beats
    col, col beats row, or says it's inconclusive. A freshly-constructed
    Outcome is blank -- all inconclusive.

    An Outcome remains logically complete. If it says that A beats B
    and B beats C, it will also say that A beats C. It never contains
    contradictions.

    Internal fields:

    higher, lower -- dicts, mapping string to dict.

    These represent the relations among candidates. higher['A'] gives you
    a set of candidates -- all the candidates that beat A. Similarly,
    lower['A'] gives you the set of candidates that lose to A.

    These mappings are filled out lazily. So if nothing is higher than
    A, then higher will not contain the key 'A'.

    (These "sets" are actually dicts, in which only the keys matter.
    Yes, I could have used Python sets here, but I didn't.)
    """

    def __init__(self, contest):
        self.contest = contest
        self.entries = contest.entries

        self.higher = {}
        self.lower = {}

    def printout(self):
        """printout() -> None

        Print out the outrankings table represented by this Outcome. Each
        entry will be '+' for a win, '-' for a loss, blank for inconclusive,
        or '`' for the diagonal.
        """

        print 'Outrankings:'
        wid = self.contest.colwidth

        print ''.rjust(wid),
        for col in self.entries:
            print col.rjust(wid),
        print

        for row in self.entries:
            print row.rjust(wid),
            for col in self.entries:
                if (col == row):
                    val = '`'
                else:
                    val = ''
                dic = self.higher.get(row)
                if (dic and dic.get(col)):
                    val += '-'
                dic = self.lower.get(row)
                if (dic and dic.get(col)):
                    val += '+'
                print str(val).rjust(wid),
            print
        print

    def result(self):
        """result() -> dict mapping string to (int, int, int)

        Return the outrankings table in the form of a dict. For each
        candidate X, dict[X] will be a tuple (wins, losses, inconclusive).
        The sum of the three integers will always be one less than the 
        number of candidates. (One less because the candidate doesn't
        challenge itself.)
        """

        total = self.contest.count - 1
        res = {}
        for row in self.entries:
            wins = 0
            losses = 0
            for col in self.entries:
                if (col == row):
                    continue
                dic = self.higher.get(row)
                if (dic and dic.get(col)):
                    losses += 1
                dic = self.lower.get(row)
                if (dic and dic.get(col)):
                    wins += 1
            res[row] = (wins, losses, total-(wins+losses))
        return res

    def printresult(self):
        """printresult() -> None

        Print the outrankings table in the form of a tally. This will be
        sorted from first place to last.
        """

        res = self.result()

        ls = list(self.entries)

        def func(key1, key2):
            # Sorting function
            (w1,l1,t1) = res[key1]
            (w2,l2,t2) = res[key2]
            val = cmp((w2,t2), (w1,t1))
            return val
        ls.sort(func)
        
        print 'Place: Name (wins, losses, unresolved)'
        wid = self.contest.colwidth
        ix = 1
        lastkey = None
        for key in ls:
            (wins, losses, ties) = res[key]
            if ((not lastkey) or func(lastkey, key)):
                place = str(ix)+':'
            else:
                place = '":'
            print place.rjust(4), key.rjust(wid), (wins, losses, ties)
            ix += 1
            lastkey = key

    def clone(self):
        """clone() -> Outcome

        Create a new Outcome identical to this one. This is a deep copy;
        further changes to one Outcome will not affect the other.
        """

        res = Outcome(self.contest)
        for key in self.higher.keys():
            res.higher[key] = self.higher[key].copy()
        for key in self.lower.keys():
            res.lower[key] = self.lower[key].copy()
        return res

    def beats(self, winner, loser):
        """beats(winner, loser) -> bool

        Returns True if winner beats loser in this Outcome. False if
        the reverse; False if it's inconclusive.
        """

        dic = self.higher.get(loser)
        if (dic and dic.get(winner)):
            return True
        return False

    def compatible(self, winner, loser):
        """compatible(winner, loser) -> bool

        Returns True if winner *could* beat loser in this Outcome --
        that is, if the contest is already true or is inconclusive. If
        the given outcome is known to be False, this returns False.

        (Really this is the same as (not beats(loser, winner)). But
        this is how I wound up implementing it.)
        """

        if (winner == loser):
            raise Exception('Entry cannot beat itself.')
        dic = self.higher.get(winner)
        if (dic and dic.get(loser)):
            return False
        dic = self.lower.get(loser)
        if (dic and dic.get(winner)):
            return False
        return True

    def accept(self, winner, loser):
        """accept(winner, loser) -> None

        Accept the fact that winner beats loser. This modifies the Outcome
        to include the new fact, *and* all consequences of that fact.
        (It's the consequences which make this method complicated.)

        If the fact causes a contradiction, this raises an Exception.
        NOTE: If you catch an Exception from this method, then the Outcome
        is left in a partially modified and inconsistent state. Do not 
        continue to use it!

        To use this method safely, you must call clone() and then call
        accept() on the copy. If any exceptions are raised, discard the
        copy and go back to the original. Once all the accept()s have
        succeeded, then you can discard the original and continue onwards
        with the copy.

        Internal logic: This keeps a list of facts to be added. Initially,
        the list contains just one fact: that winner beats loser. But
        when that fact is added, we must determine consequences: the
        winner beats everything that the loser beats, and the loser loses
        to everything that beat the winner. If any of these inferred facts
        are new to us, we add them to the list. Then we keep working until
        the list is empty.
        """

        facts = [(winner,loser)]

        while facts:
            (winner,loser) = facts.pop(0)
            if (not self.compatible(winner, loser)):
                raise Exception('Contradiction.')
            if (self.beats(winner, loser)):
                # Already known.
                continue

            # Add the new fact to the lower and higher tables.

            dic = self.lower.get(winner)
            if (not dic):
                self.lower[winner] = { loser:True }
            else:
                dic[loser] = True
            dic = self.higher.get(loser)
            if (not dic):
                self.higher[loser] = { winner:True }
            else:
                dic[winner] = True
            
            # Now, look for consequences.

            dic = self.higher.get(winner)
            if (dic):
                for key in dic.keys():
                    if (not self.beats(key, loser)):
                        facts.append( (key, loser) )
            dic = self.lower.get(loser)
            if (dic):
                for key in dic.keys():
                    if (not self.beats(winner, key)):
                        facts.append( (winner, key) )

def read_file(file, assume_complete=False):
    """read_file(filename, assume_complete=False) -> Contest

    Read in a text file describing a contest, and construct a Contest object.
    This adds the ballots (by calling addballots()), but it doesn't do
    any further computation.

    If assume_complete is True, any entries missing from a ballot are assumed
    to be tied for last.
    """

    contents = None
    ballots = []

    while True:
        ln = file.readline()
        if (not ln):
            break
        ln = ln.strip()
        if (not ln):
            continue
        if (ln.startswith('#')):
            continue
        if (ln.startswith('*')):
            if (contents):
                raise Exception('More than one line in the input file begins with *.')
            contents = ln
        else:
            ballots.append(ln)

    if (not contents):
        raise Exception('No line in the input file begins with *.')

    entries = contents[1:].split()
    if (not entries):
        raise Exception('The * line has no contents.')

    dic = {}
    for val in entries:
        dic[val] = True
    if (len(dic) != len(entries)):
        raise Exception('Duplicate entry in * line.')

    contest = Contest(entries)

    for ln in ballots:
        ls = ln.split()
        ls = [ val.split('/') for val in ls ]
        dic = {}
        for subls in ls:
            for val in subls:
                if (not contest.iskey(val)):
                    raise Exception('Unknown key in ballot: ' + val)
                if (dic.has_key(val)):
                    raise Exception('Repeated key in ballot: ' + val)
                dic[val] = True
        if (assume_complete):
            final = []
            for val in contest.entries:
                if (not dic.has_key(val)):
                    final.append(val)
            if (final):
                ls.append(final)
        contest.addballot(ls)

    return contest


# Here begins the top-level body of the script.

args = sys.argv[ 1 : ]

assume_complete = False
if ('--complete' in args):
    assume_complete = True
    args.remove('--complete')
    
if (args):
    file = open(args[0], 'rU')
else:
    file = sys.stdin

try:
    contest = read_file(file, assume_complete)
except Exception, ex:
    print ex
    sys.exit(1)
    
if (file != sys.stdin):
    file.close()

# Do all the computation, and print the result.

#contest.printballots()
contest.computemargins()
contest.printmargins()

outcome = contest.compute()
outcome.printout()
outcome.printresult()
