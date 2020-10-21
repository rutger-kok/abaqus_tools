'''
Script to replace a string within a file with a different string.
'''

from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

def replace(file_path, string_to_replace, new_string):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(string_to_replace, new_string))
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

if __name__ == '__main__':
    replace('C:\\Workspace\\example.py', 'example', 'newName')