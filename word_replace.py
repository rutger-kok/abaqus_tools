'''
Script to convert Matlab jacobian terms to Fortran format.
'''

import sys
import os
import re

def main():
    input_file = sys.argv[1]  # path to file with equations to be wrapped
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):  # check if input file exists
        print('File {} does not exist.'.format(input_file))
        sys.exit()

    # open input file
    with open(input_file, 'r') as reader:
        content = reader.read()
    content = re.sub(r"\b0.5000\b","OHPOINTFIVE", content)
    content = re.sub(r"\b0.2500\b","OHPOINTTWOFIVE", content)
    content = re.sub(r"\b1.5000\b","ONEPOINTFIVE", content)
    content = re.sub(r"\b1\b","1.0d0", content)
    content = re.sub(r"\b2\b","2.0d0", content)
    content = re.sub(r"\b3\b","3.0d0", content)
    content = re.sub(r"\b4\b","4.0d0", content)
    content = re.sub(r"\b16\b","16.0d0", content)
    content = re.sub(r"\b64\b","64.0d0", content)
    content = re.sub(r"\b8\b","8.0d0", content)
    content = re.sub(r"\b32\b","32.0d0", content)
    content = re.sub(r"\bOHPOINTFIVE\b","0.5d0", content)
    content = re.sub(r"\bOHPOINTTWOFIVE\b","0.25d0", content)
    content = re.sub(r"\bONEPOINTFIVE\b","1.5d0", content)
    content = content.replace(r'^', r'**')
    content = content.replace(r'sin(x)', r'n')
    content = content.replace(r'sin(2.0d0*x)', r'2*m*n')
    content = content.replace(r'cos(x)', r'm')
    content = content.replace(r'sign(', r'sign(1.0d0,')
    content = re.sub(r"\bec12\b","ec_cr\x284\x29", content)
    content = re.sub(r"\bec22\b","ec_cr\x282\x29", content)
    content = re.sub(r"\bec33\b","ec_cr\x283\x29", content)
    content = re.sub(r"\bec23\b","ec_cr\x285\x29", content)
    content = re.sub(r"\be22\b","eTotal_cr\x282\x29", content)
    content = re.sub(r"\be33\b","eTotal_cr\x283\x29", content)
    content = re.sub(r"\be23\b","eTotal_cr\x285\x29", content)
    content = re.sub(r"\bestiff22\b","E22", content)
    content = re.sub(r"\btbar_1\b","tbar_cr\x281\x29", content)
    content = re.sub(r"\btbar_2\b","tbar_cr\x282\x29", content)
    content = re.sub(r"\btbar_3\b","tbar_cr\x283\x29", content)
    content = re.sub(r"\bC44\b","C\x284,4\x29", content)
    content = re.sub(r"\bC55\b","C\x285,5\x29", content)
    content = re.sub(r"\bC66\b","C\x286,6\x29", content)
    content = re.sub(r"\bC23\b","C\x282,3\x29", content)
    content = re.sub(r"\bC22\b","C\x282,2\x29", content)
    content = re.sub(r"\bC33\b","C\x283,3\x29", content)
    content = re.sub("A\x281.0d0,1.0d0\x29","A\x281,1\x29", content)
    content = re.sub("A\x281.0d0,2.0d0\x29","A\x281,2\x29", content)
    content = re.sub("A\x281.0d0,3.0d0\x29","A\x281,3\x29", content)
    content = re.sub("A\x282.0d0,1.0d0\x29","A\x282,1\x29", content)
    content = re.sub("A\x282.0d0,2.0d0\x29","A\x282,2\x29", content)
    content = re.sub("A\x282.0d0,3.0d0\x29","A\x282,3\x29", content)
    content = re.sub("A\x283.0d0,1.0d0\x29","A\x283,1\x29", content)
    content = re.sub("A\x283.0d0,2.0d0\x29","A\x283,2\x29", content)
    content = re.sub("A\x283.0d0,3.0d0\x29","A\x283,3\x29", content)
    content = re.sub(r"\b(1.0d0/2.0d0)\b","0.5d0", content)
    with open(output_file, 'w') as writer:
        writer.write(content)


if __name__ == '__main__':
    main()
