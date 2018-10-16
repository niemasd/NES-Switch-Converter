#! /usr/bin/env python3
'''
Convert an image to TGA
'''
from sys import argv
from PIL import Image
if len(argv) != 2:
    print("Usage: %s inputfile"%argv[0]); exit(1)
Image.open(argv[1]).save('%s.tga'%'.'.join(argv[1].split('.')[:-1]))
