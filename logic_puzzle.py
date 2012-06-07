#!/usr/bin/python

"""
UNIT 2: Logic Puzzle

You will write code to solve the following logic puzzle:

1. The person who arrived on Wednesday bought the laptop.
2. The programmer is not Wilkes.
3. Of the programmer and the person who bought the droid,
   one is Wilkes and the other is Hamming. 
4. The writer is not Minsky.
5. Neither Knuth nor the person who bought the tablet is the manager.
6. Knuth arrived the day after Simon.
7. The person who arrived on Thursday is not the designer.
8. The person who arrived on Friday didn't buy the tablet.
9. The designer didn't buy the droid.
10. Knuth arrived the day after the manager.
11. Of the person who bought the laptop and Wilkes,
    one arrived on Monday and the other is the writer.
12. Either the person who bought the iphone or the person who bought the tablet
    arrived on Tuesday.

You will write the function logic_puzzle(), which should return a list of the
names of the people in the order in which they arrive. For example, if they
happen to arrive in alphabetical order, Hamming on Monday, Knuth on Tuesday, etc.,
then you would return:

['Hamming', 'Knuth', 'Minsky', 'Simon', 'Wilkes']

(You can assume that the days mentioned are all in the same week.)
"""

from itertools import permutations as perm

def logic_puzzle():
    "Return a list of the names of the people, in the order they arrive."
    Monday, Tuesday, Wednesday, Thursday, Friday = 0, 1, 2, 3, 4
    days = list(perm(range(5)))
    # compute puzzle
    (Hamming, Knuth, Minsky, Simon, Wilkes) = next((Hamming, Knuth, Minsky, Simon, Wilkes)
        for (Hamming, Knuth, Minsky, Simon, Wilkes) in days
        for (programmer, designer, writer, manager, _) in days
        for (droid, tablet, iphone, laptop, _) in days
        if laptop == Wednesday #1
        if Wilkes != programmer #2
        if (programmer, droid) in perm([Wilkes, Hamming]) #3
        if writer != Minsky #4
        if Knuth != manager and tablet != manager #5
        if Knuth == Simon + 1 #6 
        if designer != Thursday #7
        if Friday != tablet #8
        if designer != droid #9
        if Knuth == manager + 1 #10
        if (laptop, Wilkes) in perm ([Monday, writer]) #11
        if iphone == Tuesday or tablet == Tuesday #12
        )
    # humanize solution
    result = [''] * 5
    result[Hamming] = 'Hamming'
    result[Knuth] = 'Knuth'
    result[Minsky] = 'Minsky'
    result[Simon] = 'Simon'
    result[Wilkes] = 'Wilkes'
    return result
            
print logic_puzzle()

