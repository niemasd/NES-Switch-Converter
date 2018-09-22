#! /usr/bin/env python3
'''
Zlib decompress a file
'''
from sys import argv
from zlib import decompress
if len(argv) != 2:
    print("Usage: %s inputfile"%argv[0]); exit(1)
assert argv[1][-2:].lower() == '.z', "Input file must end in .z"
f = open(argv[1][:-2],'wb'); f.write(decompress(open(argv[1],'rb').read())); f.close()
