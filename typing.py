# !/usr/bin/python3
# -*- coding: utf-8 -*-#
#
#  Jander Moreira
#
#  Typing code animation
from os import system, getpid
from random import randint
import re

from pygments import highlight
from pygments import lexers
from terminal import ImageFormatter
from pygments.styles import get_style_by_name


class CodeSegments:
    def __init__(self, source_code = '', language = 'C', style = 'zenburn'):
        self.scene_counter = 0
        self.language = language
        self.source_code = source_code
        self.code_segments = self.segment_code(source_code)
        self.style = style

    def segment_code(self, source_code):
        source_code = source_code.replace('\n', '@newline@')

        match_result = True
        code_segments = []
        while match_result:
            match_result = re.search(r'@(from|only):(\d)>(.*?)<(from|only)@',
                                     source_code)
            if match_result:
                if match_result.group(1) != match_result.group(4):
                    print('Unbalanced markup tags')
                    exit(1)
                previous_text = source_code[:match_result.span()[0]]
                if len(previous_text) > 0:
                    code_segments.append(
                        {'class': 'text', 'scene': 0,
                         'code': previous_text.replace('@newline@', '\n')})
                source_code = source_code[match_result.span()[1]:]
                code_segments.append({'class': match_result.group(1),
                                      'scene': int(match_result.group(2)),
                                      'code': match_result.group(3).replace(
                                          '@newline@', '\n')})
                if int(match_result.group(2)) > self.scene_counter:
                    self.scene_counter = int(match_result.group(2))

        if len(source_code) > 0:
            code_segments.append(
                {'class': 'text', 'scene': 0,
                 'code': source_code.replace('@newline@', '\n')})

        return code_segments

    def code_scene(self, scene_number):
        segments = [seg for seg in self.code_segments if
                    seg['class'] == 'text' or seg['class'] == 'from' and seg[
                        'scene'] <= scene_number or seg['class'] == 'only' and
                    seg['scene'] == scene_number]
        code = ''
        for seg in segments:
            code += seg['code']

        return code

    def _typing_step(self):
        return randint(1, 3)

    def animate_scene(self, scene_number):
        lexer = lexers.get_lexer_by_name(self.language)

        image_sequence = []
        if scene_number == 0:
            # animate base code
            print(']]]]] base code')
            source_code = ''.join([seg['code'] for seg in self.code_segments
                                   if seg['class'] == 'text'])
            typing_position = 0
            while typing_position < len(source_code):
                typing_position += self._typing_step()
                formatter = ImageFormatter(full = True,
                                           style = get_style_by_name(
                                               self.style))
                image_sequence.append(
                    highlight(source_code[:typing_position + 1] + '_',
                              lexer, formatter))
            formatter = ImageFormatter(full = True,
                                       style = get_style_by_name(
                                           self.style))
            image_sequence.append(highlight(source_code, lexer, formatter))
            # print(source_code)

        else:
            segments = [seg for seg in self.code_segments if
                        seg['class'] == 'text' or seg['class'] == 'from' and
                        seg['scene'] <= scene_number or seg[
                            'class'] == 'only' and seg['scene'] == scene_number]
            animations_indexes = [idx for (idx, seg) in enumerate(segments) if
                                  seg['class'] != 'text' and
                                  seg['scene'] == scene_number]
            # print(']]]', animations_counter, 'animations in this scene:',
            #       animations_indexes)

            for animated_segment in animations_indexes:
                preceding_code = ''.join(
                    [seg['code'] for seg in segments[:animated_segment]])
                animated_code = segments[animated_segment]['code']
                following_code = ''.join(
                    [seg['code'] for seg in segments[animated_segment + 1:] if
                     seg['class'] == 'text' or
                     seg['class'] in ['from', 'only'] and
                     seg['scene'] < scene_number])

                typing_position = 0
                while typing_position <= len(animated_code):
                    # print(typing_position, '', end = '')
                    typing_position += self._typing_step()
                    formatter = ImageFormatter(full = True,
                                               style = get_style_by_name(
                                                   self.style))
                    image_sequence.append(highlight(
                        preceding_code +
                        animated_code[:typing_position + 1] + '_' +
                        following_code, lexer, formatter))

                # print('---------------- antes\n', preceding_code)
                # print('---------------- animado\n', animated_code)
                # print('---------------- depois\n', following_code)

                formatter = ImageFormatter(full = True,
                                           style = get_style_by_name(
                                               self.style))
                image_sequence.append(highlight(
                    preceding_code + animated_code + following_code,
                    lexer, formatter))
        return image_sequence

    def animate(self, timeline, verbose = True):
        temp_prefix = f'/tmp/typing.tmp.{getpid()}_'
        scene_frames_count = []
        concatation = ''
        for scene in range(self.scene_counter + 1):
            if verbose:
                print(f'> Scene #{scene}:\n  - Creating frames', end = '')
            scene_frames = self.animate_scene(scene)
            scene_frames_count.append(len(scene_frames))
            if verbose: print('\n  - Saving frames: ')
            for count, frame in enumerate(scene_frames):
                if verbose: print(f'\tFrame {count:03d}')
                open(temp_prefix + f'{scene:02d}_{count:03d}.png', 'wb').write(
                    frame)

            if verbose: print('\tCreating clip (animation)')
            frame_rate_animation = scene_frames_count[scene] / \
                                   timeline[scene][0]
            system('ffmpeg -nostdin ' +
                   f'-r {frame_rate_animation:.5f} -f image2 -i ' +
                   temp_prefix + f'{scene:02d}_%3d.png' +
                   ' -vf fps=30' +
                   f' -vcodec libx264 -s 1280x720' +
                   f' {temp_prefix}{scene:02d}_anim.mp4' +
                   ' >> /tmp/log 2> /dev/null')
            concatation += f"file '{temp_prefix}{scene:02d}_anim.mp4'\n"

            if timeline[scene][1] != 0:
                if verbose: print('\tCreating clip (pause)')
                frame_rate_pause = 1 / timeline[scene][1]
                system('ffmpeg -nostdin -loop 1 -i ' +
                       temp_prefix +
                       f'{scene:02d}_{scene_frames_count[scene] - 1:03d}.png' +
                       ' -vf fps=30' +
                       f' -vcodec libx264 -t {timeline[scene][1]}' +
                       ' -s 1280x720' +
                       f' {temp_prefix}{scene:02d}_pause.mp4' +
                       ' >> /tmp/log 2> /dev/null')
            concatation += f"file '{temp_prefix}{scene:02d}_pause.mp4'\n"
        if verbose: print("< ")

        # final video
        if verbose:
            print('> Creating video')
            print('  - Creating concatenation file')
        open(temp_prefix + 'concat.txt', 'w').write(concatation)
        if verbose: print('  - Concatenating clips', end = '')
        system(f'ffmpeg -nostdin -f concat -safe 0 -i ' + temp_prefix +
               f'concat.txt -c copy -y code_{getpid()}.mp4' +
               ' >> /tmp/log 2> /dev/null')
        if verbose: print('\n<')

        # cleanup
        system(f'rm -f {temp_prefix}*.png')


def main():
    source_code = open('hello.c', 'r').read()
    segments = CodeSegments(source_code)
    for s in segments.code_segments:
        print(s)
    # for s in range(segments.scene_counter + 1):
    #     print('========================== ', s, '===========')
    #     segments.animate_scene(s)
    segments.animate([
        (1, 1),
        (1, 1),
        (1, 1),
        (1, 1),
        (1, 1),
    ])


if __name__ == '__main__':
    main()
