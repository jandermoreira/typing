#!/usr/bin/python3
# -*- coding: utf-8 -*-#
#
#  Jander Moreira
#
#  Typing code animation
import sys
from pytyping import pytyping as pt
from pygments.styles import get_all_styles


def main():
    # for i in get_all_styles():
    #     print(i)
    source_code = open(sys.argv[1], 'r').read()
    segments = pt.Typing(source_code, style = 'native')
    segments.animate(verbose = True)


if __name__ == '__main__':
    main()
