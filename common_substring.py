'''
Brute force method to determine the most frequently occurring substrings in a
file. For very large files consider breaking it into more manageable chunks
first.

Adapted from: https://stackoverflow.com/questions/25071766/find-most-common-sub-string-pattern-in-a-file
Last modified: 10/02/2021
'''

import sys
import os
from collections import Counter


def main():
    input_file = sys.argv[1]  # path to file with equations to be wrapped
    min_length = int(sys.argv[2])  # minimum length of substring
    max_length = int(sys.argv[3])  # maximum length of substring

    if not os.path.isfile(input_file):  # check if input file exists
        print('File {} does not exist.'.format(input_file))
        sys.exit()

    # open input file
    with open(input_file, 'r') as reader:
        content = reader.read()
    for n in range(min_length, max_length):
        substr_counter = Counter(content[i: i+n] for i in range(len(content) - n))
        phrase, count = substr_counter.most_common(1)[0]
        if count == 1:      # early out for trivial cases
            break
        print 'Size: %3d:  Occurrences: %3d  Phrase: %r' % (n, count, phrase)

if __name__ == '__main__':
    main()
