#!/usr/bin/python3
# -*- coding: utf-8 -*-#
#
#  Jander Moreira
#
#  Typing code animation
import sys
from pytyping import pytyping as pt


def main():
    source_code = open(sys.argv[1], 'r').read()
    try:
        segments = pt.Typing(source_code, style = 'friendly')
    except pt.TypingNoTimeline:
        print('No timeline found')
    except pt.TypingUnbalancedMarkup:
        print('Unbalanced tag pairs found')
    else:
        ''' run! '''
        # for s in segments.code_segments:
        #     print(s)

        # for s in range(segments.scene_counter + 1):
        #     print('------------------------', s)
        #     print(segments.code_scene(s))
        # print(segments.code_scene(3))

        # for s in range(segments.scene_counter + 1):
        #     print('========================== ', s, '===========')
        #     segments.animate_scene(s)
        segments.animate(verbose = True)
        # open('f.svg', 'w').write(segments.animate_scene(0)[0]['frames'][-1])


if __name__ == '__main__':
    main()
