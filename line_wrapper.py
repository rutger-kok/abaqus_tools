'''
Fortran Line Wrapper - script file to wrap Fortran equations to specified
number of characters per line. Lines are split at +, -, *, or / signs.

line_length = max number of characters on a single line (e.g. 72 for free
format Fortran (Fortran 90))
input_file = file with each equation on a new line
output_file = file in which each equation from the input_file is wrapped
to the number of characters specified in line_length.

Continuation lines are indented by a 2 spaces relative to the first line
of the equation. For Fortran 90 " &" is appended to each line. For Fortran
77, numbers are placed in column 7 for continuation.

Last modified: 22/02/2021
(c) Rutger Kok
'''

import sys
import os
import re
from itertools import cycle


def fortran_77_output(input_file, output_file):
    # max length must account for continuation line indent
    max_length = 61  # 72 - 7 - 4 (cont. line indent)
    with open(output_file, 'w') as writer:
        for line in split_lines(input_file, max_length):
            # continuation line numbering
            line_numbers = cycle([1, 2, 3, 4, 5, 6, 7, 8, 9])
            for i, output_line in enumerate(line):
                if i == 0:
                    output = ' ' * 8 + output_line + '\n'
                else:
                    n = str(next(line_numbers))
                    output = ' ' * 5 + n + ' ' * 4 + output_line + '\n'
                writer.write(output)


def fortran_90_output(input_file, output_file):
    # max length must account for continuation line indent
    max_length = 128  # 132 - 2 - 2 (cont. line indent)
    lines = split_lines(input_file, max_length)
    with open(output_file, 'w') as writer:
        for line in split_lines(input_file, max_length):
            for i, output_line in enumerate(lines):
                if i == 0:
                    output = output_line + ' &\n'
                elif i == len(lines):
                    output = output_line + '\n'
                else:
                    output = ' ' * 2 + output_line + ' &\n'
                writer.write(output)


def split_lines(input_file, max_length):
    with open(input_file, 'r') as reader:
        for input_line in reader:  # iterate over lines in the input file
            # define regular expression to split lines
            r = r'.{1,' + str(max_length) + r'}(?:\+|\-|\/|(?<!\*)\*(?!\*)|$)'
            # create a list of lines split according to the regular expression
            short_lines = [x.strip() for x in re.findall(r, input_line)]
            yield short_lines


def main():
    input_file = sys.argv[1]  # path to file with equations to be wrapped
    output_file = sys.argv[2]  # new file path with wrapped equations
    version = sys.argv[3]  # '77' for fixed format, '90' for free format

    if not os.path.isfile(input_file):  # check if input file exists
        print('File {} does not exist.'.format(input_file))
        sys.exit()

    if int(version) == 77:
        fortran_77_output(input_file, output_file)
    else:
        fortran_90_output(input_file, output_file)


if __name__ == '__main__':
    main()
