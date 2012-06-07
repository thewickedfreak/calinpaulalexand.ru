#!/usr/bin/python
"""
In the game of darts, players throw darts at a board to score points.
The circular board has a 'bulls-eye' in the center and 20 slices
called sections, numbered 1 to 20, radiating out from the bulls-eye.
The board is also divided into concentric rings.  The bulls-eye has
two rings: an outer 'single' ring and an inner 'double' ring.  Each
section is divided into 4 rings: starting at the center we have a
thick single ring, a thin triple ring, another thick single ring, and
a thin double ring.  A ring/section combination is called a 'target';
they have names like 'S20', 'D20' and 'T20' for single, double, and
triple 20, respectively; these score 20, 40, and 60 points. The
bulls-eyes are named 'SB' and 'DB', worth 25 and 50 points
respectively. Illustration (png image): http://goo.gl/i7XJ9

There are several variants of darts play; in the game called '501',
each player throws three darts per turn, adding up points until they
total exactly 501. However, the final dart must be in a double ring.

Your first task is to write the function double_out(total), which will
output a list of 1 to 3 darts that add up to total, with the
restriction that the final dart is a double. See test_darts() for
examples. Return None if there is no list that achieves the total.

Often there are several ways to achieve a total.  You must return a
shortest possible list, but you have your choice of which one. For
example, for total=100, you can choose ['T20', 'D20'] or ['DB', 'DB']
but you cannot choose ['T20', 'D10', 'D10'].
"""

def test_darts():
    "Test the double_out function."
    assert double_out(170) == ['T20', 'T20', 'DB']
    assert double_out(171) == None
    assert double_out(100) in (['T20', 'D20'], ['DB', 'DB'])
    print 'Halfway done!'

"""
My strategy: I decided to choose the result that has the highest valued
target(s) first, e.g. always take T20 on the first dart if we can achieve
a solution that way.  If not, try T19 first, and so on. At first I thought
I would need three passes: first try to solve with one dart, then with two,
then with three.  But I realized that if we include 0 as a possible dart
value, and always try the 0 first, then we get the effect of having three
passes, but we only have to code one pass.  So I creted ordered_points as
a list of all possible scores that a single dart can achieve, with 0 first,
and then descending: [0, 60, 57, ..., 1].  I iterate dart1 and dart2 over
that; then dart3 must be whatever is left over to add up to total.  If
dart3 is a valid element of points, then we have a solution.  But the
solution, is a list of numbers, like [0, 60, 40]; we need to transform that
into a list of target names, like ['T20', 'D20'], we do that by defining name(d)
to get the name of a target that scores d.  When there are several choices,
we must choose a double for the last dart, but for the others I prefer the
easiest targets first: 'S' is easiest, then 'T', then 'D'.
"""

def name(d):
    "Return the type of a throw that achieves the inputed value."
    if d == 50: return 'DB'
    if d == 25: return 'SB'
    if d <= 40 and not d % 2: return 'D' + str(d/2)
    if d <= 60 and not d % 3: return 'T' + str(d/3)
    if d < 20: return 'S' + str(d)
    else: raise ValueError('Recieved value %s which iz not okai.' %str(d))

def valid_last(d):
    "check if the inputed score is a valid last throw (is a double shot)"
    if d <= 40 and d % 2 == 0 or d == 50: return True
    return False

def valid_game(throws,total):
    "Checks whether the throws sum to the total and the last throw is a double"
    if sum(throws) == total and valid_last(throws[-1]):
        return True
    return False

def improve_result(result, scores):
    "Update the result if the given scores represent a better throw"
    scores = [i for i in scores if i > 0]
    if not result or len(scores)<len(result):
        result = scores
    return result

def fancy(result):
    "Make the throws more expressive."
    return [name(i) for i in result]     

def double_out(total):
    """Return a shortest possible list of targets that add to total,
    where the length <= 3 and the final element is a double.
    If there is no solution, return None."""
    # compute possible throws
    ordered_points = set([])
    for i in range(1,21):
        ordered_points |= set([i, 2 * i, 3 * i])
    ordered_points |= set([25, 50])
    ordered_points = list(ordered_points)
    ordered_points.sort(reverse=True)
    ordered_points = [0] + ordered_points
    # initialize result
    result = []
    # generate throws
    for i in ordered_points:
        for j in ordered_points:
            for k in ordered_points:
                if valid_game((i,j,k),total):
                    result = improve_result(result,(i,j,k))
    return fancy(result) or None 

"""
It is easy enough to say "170 points? Easy! Just hit T20, T20, DB."
But, at least for me, it is much harder to actually execute the plan
and hit each target.  In this second half of the question, we
investigate what happens if the dart-thrower is not 100% accurate.

We will use a wrong (but still useful) model of inaccuracy. A player
has a single number from 0 to 1 that characterizes his/her miss rate.
If miss=0.0, that means the player hits the target every time.
But if miss is, say, 0.1, then the player misses the section s/he
is aiming at 10% of the time, and also (independently) misses the thin
double or triple ring 10% of the time. Where do the misses go?
Here's the model:

First, for ring accuracy.  If you aim for the triple ring, all the
misses go to a single ring (some to the inner one, some to the outer
one, but the model doesn't distinguish between these). If you aim for
the double ring (at the edge of the board), half the misses (e.g. 0.05
if miss=0.1) go to the single ring, and half off the board. (We will
agree to call the off-the-board 'target' by the name 'OFF'.) If you
aim for a thick single ring, it is about 5 times thicker than the thin
rings, so your miss ratio is reduced to 1/5th, and of these, half go to
the double ring and half to the triple.  So with miss=0.1, 0.01 will go
to each of the double and triple ring.  Finally, for the bulls-eyes. If
you aim for the single bull, 1/4 of your misses go to the double bull and
3/4 to the single ring.  If you aim for the double bull, it is tiny, so
your miss rate is tripled; of that, 2/3 goes to the single ring and 1/3
to the single bull ring.

Now, for section accuracy.  Half your miss rate goes one section clockwise
and half one section counter-clockwise from your target. The clockwise 
order of sections is:

    20 1 18 4 13 6 10 15 2 17 3 19 7 16 8 11 14 9 12 5

If you aim for the bull (single or double) and miss on rings, then the
section you end up on is equally possible among all 20 sections.  But
independent of that you can also miss on sections; again such a miss
is equally likely to go to any section and should be recorded as being
in the single ring.

You will need to build a model for these probabilities, and define the
function outcome(target, miss), which takes a target (like 'T20') and
a miss ration (like 0.1) and returns a dict of {target: probability}
pairs indicating the possible outcomes.  You will also define
best_target(miss) which, for a given miss ratio, returns the target 
with the highest expected score.

If you are very ambitious, you can try to find the optimal strategy for
accuracy-limited darts: given a state defined by your total score
needed and the number of darts remaining in your 3-dart turn, return
the target that minimizes the expected number of total 3-dart turns
(not the number of darts) required to reach the total.  This is harder
than Pig for several reasons: there are many outcomes, so the search space 
is large; also, it is always possible to miss a double, and thus there is
no guarantee that the game will end in a finite number of moves.
"""

LAYOUT = (20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11,
     14, 9, 12, 5)

def get_neighbours(section):
    "Return the 2 neighbours of a section as a tuple."
    # parameter check
    if not isinstance(section, int):
        try:
            section = int(section)
        except:
            raise ValueError
    for i in range(len(LAYOUT)):
        if LAYOUT[i] == section:
            return (str(LAYOUT[i-1]),str(LAYOUT[(i+1)%len(LAYOUT)]))
def ring_outcome(target, miss):
    "Return the probability distribution for rings"
    result = {}
    if target == 'SB':
        result['SB'] = 1 - miss
        result['S'] = 3*miss/4
        result['DB'] = miss/4
    elif target == 'DB':
        result['DB'] = 1 - miss
        result['S'] = 2*miss/3
        result['SB'] = miss/3
    elif 'T' in target:
        result['T'] = 1 - miss
        result['S'] = miss
    elif 'D' in target:
        result['S'] = miss/2
        result['OFF'] = miss/2
        result['D'] = 1 - miss
    elif 'S' in target:
        result['D'] = miss/10
        result['T'] = miss/10
        result['S'] = 1 - miss/5
    return result   

def score(target):
    if target == 'SB':
        return 25
    if target == 'DB':
        return 50
    if 'T' in target: multiplier = 3
    elif 'D' in target: multiplier = 2
    else: multiplier = 1
    return int(target[1:])*multiplier

def section_outcome(target, miss):
    "Return the probability distribution for sections"
    result = {}
    if 'B' in target:
        result['B'] = 1 - miss
        for i in range(len(LAYOUT)):
            result[str(i+1)] = miss / len(LAYOUT)        
    else:
        left, right = get_neighbours(target[1:])
        result[left] = miss/2
        result[right] = miss/2
        result[target[1:]] = 1 - miss
    return result 

def outcome(target, miss):
    "Return a probability distribution of [(target, probability)] pairs."
    rings = ring_outcome(target, miss)
    sections = section_outcome(target, miss)
    result = {}
    for r in rings.items():
        for s in sections.items():
            if r[0] == 'OFF': continue
            if r[0] in ('SB', 'DB'):
                if s[0] == 'B':
                    result[r[0]] = r[1] * s[1] + result.get(r[0], 0)
                else:
                    continue
            else:
                if not 'B' in target:
                    key = r[0]+s[0]
                    result[key] = r[1] * s[1] + result.get(key, 0) 
                else:
                    if s[0] != 'B':
                        key = r[0] + s[0]
                        result[key] = r[1] * (1-miss)/20 + s[1]  + result.get(key, 0)
    return result

def best_target(miss):
    "Return the target that maximizes the expected score."
    ordered_points = set([])
    for i in range(1,21):
        ordered_points |= set([i, 2 * i, 3 * i])
    ordered_points |= set([25, 50])
    ordered_points = list(ordered_points)
    ordered_points.sort(reverse=True)
    targets = [name(i) for i in ordered_points]
    maxout, max_t = 0, 0
    for t in targets:
        hits = outcome(t, miss)
        aux = sum([score(i)*j for i, j in hits.items()])
        if aux > maxout:
            maxout = aux
            max_t = t
    return max_t

def same_outcome(dict1, dict2):
    "Two states are the same if all corresponding sets of locs are the same."
    return all(abs(dict1.get(key, 0) - dict2.get(key, 0)) <= 0.0001
               for key in set(dict1) | set(dict2))

def test_darts2():
    assert same_outcome(outcome('T20', 0.0), {'T20': 1.0})
    assert same_outcome(outcome('T20', 0.1), 
                        {'T20': 0.81, 'S1': 0.005, 'T5': 0.045, 
                         'S5': 0.005, 'T1': 0.045, 'S20': 0.09})
    assert (same_outcome(
            outcome('SB', 0.2),
            {'S9': 0.016, 'S8': 0.016, 'S3': 0.016, 'S2': 0.016, 'S1': 0.016,
             'DB': 0.04, 'S6': 0.016, 'S5': 0.016, 'S4': 0.016, 'S20': 0.016,
             'S19': 0.016, 'S18': 0.016, 'S13': 0.016, 'S12': 0.016, 'S11': 0.016,
             'S10': 0.016, 'S17': 0.016, 'S16': 0.016, 'S15': 0.016, 'S14': 0.016,
             'S7': 0.016, 'SB': 0.64}))
    assert best_target(0.0) == 'T20'
    assert best_target(0.1) == 'T20'
    assert best_target(0.4) == 'T19'

def test_outcomes():
    assert same_outcome(ring_outcome('SB', .2), {'SB': 0.8, 'S': 0.15, 'DB': 0.05})
    assert same_outcome(ring_outcome('S20', .2), {'S': 0.96, 'D': 0.02, 'T': 0.02})
    assert same_outcome(section_outcome('S20', .2), {'1': 0.1, '5': 0.1, '20': 0.8})
    assert same_outcome(section_outcome('SB', .2), {'B': 0.8, '11': 0.01, '10': 0.01, 
        '13': 0.01, '20': 0.01, '14': 0.01, '17': 0.01, '16': 0.01, '19': 0.01, 
        '18': 0.01, '1': 0.01, '3': 0.01, '2': 0.01, '5': 0.01, '4': 0.01, '7': 0.01, 
        '6': 0.01, '9': 0.01, '15': 0.01, '12': 0.01, '8': 0.01})

test_darts()
test_outcomes()
test_darts2()
