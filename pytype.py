# !/usr/bin/python3
# -*- coding: utf-8 -*-#
#
#  Jander Moreira
#
#  Typing code animation
from pytyping.pytyping import Typing


def main():
    source_code = open('samples/hellonew.c', 'r').read()
    try:
        segments = Typing(source_code, style = 'monokai')
    except TypingNoTimeline:
        print('No timeline found')
    except TypingUnbalancedMarkup:
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
        # segments.animate_scene(3)


if __name__ == '__main__':
    main()
