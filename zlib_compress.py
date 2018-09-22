#! /usr/bin/env python3
'''
Zlib compress a file
'''
from sys import argv
from zlib import compress
if len(argv) != 2:
    print("Usage: %s inputfile"%argv[0]); exit(1)
f = open("%s.z"%argv[1],'wb'); f.write(compress(open(argv[1],'rb').read(),9)); f.close()
