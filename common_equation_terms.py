'''
Brute force method to determine the most frequently occurring parts of
equations bounded by brackets. Lists most frequently occuring parts of
equations in a file and the potential savings from factorizing. 

Adapted from: https://stackoverflow.com/questions/25071766/find-most-common-sub-string-pattern-in-a-file
Last modified: 10/02/2021
'''

import sys
import os
import re
from collections import Counter

def main():
    input_file = sys.argv[1]  # path to file with equations to be wrapped
    min_length = int(sys.argv[2])  # minimum length of substring
    max_length = int(sys.argv[3])  # maximum length of substring
    verbose = int(sys.argv[4])

    if not os.path.isfile(input_file):  # check if input file exists
        print('File {} does not exist.'.format(input_file))
        sys.exit()

    # open input file
    substrings = []
    with open(input_file, 'r') as reader:
        for line in reader:
            for openpos, closepos, level in matches(line):
                if (closepos - openpos > min_length) and (closepos - openpos < max_length):
                    substrings.append(line[openpos:closepos])
    substring_reps = Counter(substrings)
    sorted_by_savings = {(count-1)*len(phrase): phrase for (phrase, count) in substring_reps.iteritems()}
    keys_sorted = sorted(sorted_by_savings.keys())
    for savings in keys_sorted:
        if verbose:
            print savings, '------->', sorted_by_savings[savings], '------->', len(sorted_by_savings[savings])
        else:
            print savings, '------->', sorted_by_savings[savings][0:40], '------->', len(sorted_by_savings[savings])


def matches(line, opendelim='(', closedelim=')'):
    '''
    Function to match expressions enclosed by nested parentheses.
    From: https://stackoverflow.com/questions/5454322/python-how-to-match-nested-parentheses-with-regex
    '''
    stack = []
    for m in re.finditer(r'[{}{}]'.format(opendelim, closedelim), line):
        pos = m.start()
        if line[pos-1] == '\\':
            # skip escape sequence
            continue
        c = line[pos]
        if c == opendelim:
            stack.append(pos+1)
        elif c == closedelim:
            if len(stack) > 0:
                prevpos = stack.pop()
                # print("matched", prevpos, pos, line[prevpos:pos])
                yield (prevpos, pos, len(stack))
            else:
                # error
                print "encountered extraneous closing quote at pos {}: '{}'".format(pos, line[pos:])
                pass
    if len(stack) > 0:
        for pos in stack:
            print "expecting closing quote to match open quote starting at: '{}'".format(line[pos-1:])


if __name__ == '__main__':
    main()
