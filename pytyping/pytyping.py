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
# from formatter import SvgFormatter
from pytyping.svgformatter import SvgFormatter
from pygments.styles import get_style_by_name


class TypingNoTimeline(Exception):
    '''No timeline'''


class TypingUnbalancedMarkup(Exception):
    '''Unbalanced markup tags'''


class Typing:
    def __init__(self, source_code = '', language = 'C', style = 'default'):
        self.scene_counter = 0
        self.language = language
        self.lexer = lexers.get_lexer_by_name(self.language)
        self.source_code = source_code
        self.code_segments = self.segment_code(source_code)
        print(style, '<<<<<<<<<<<<<<<<<<<<<<<<<<')
        self.style = get_style_by_name(style)

    def segment_code(self, source_code):
        source_code = source_code.replace('\n', '@newline@')

        # Get base times
        match_result = re.search(r'@base: \((.*?)\)@', source_code)
        if not match_result:
            base_time = [3., 10.]
        else:
            # todo: add an exception to handle str to float conversion
            base_time = [float(t) for t in match_result.group(1).split(',')]
            source_code = source_code.replace(match_result.group(0), '')

        # Get code segments
        match_result = True
        code_segments = []
        while match_result:
            match_result = re.search(
                r'@(from|only):([\d]+)[\s]*\((.*?)\)>(.*?)<(from|only)@',
                source_code)
            if match_result:
                if match_result.group(1) != match_result.group(5):
                    raise TypingUnbalancedMarkup
                segment = {'class': match_result.group(1),
                           'scene': int(match_result.group(2)),
                           'time': [float(t) for t in
                                    match_result.group(3).split(',')],
                           'code': match_result.group(4).replace('@newline@',
                                                                 '\n')}
                previous_text = source_code[:match_result.span()[0]]
                if len(previous_text) > 0:
                    code_segments.append(
                        {'class': 'text',
                         'scene': 0,
                         'time': base_time,
                         'code': previous_text.replace('@newline@', '\n')})
                source_code = source_code[match_result.span()[1]:]
                code_segments.append(segment)
                if segment['scene'] > self.scene_counter:
                    self.scene_counter = segment['scene']

        if len(source_code) > 0:
            code_segments.append(
                {'class': 'text',
                 'scene': 0,
                 'time': base_time,
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

    @staticmethod
    def _typing_step():
        return randint(1, 3)

    def _typo(self):
        if randint(1, 100) <= 10:  # 25%
            return ''.join([chr(randint(ord('a'), ord('z')))
                            for n in range(randint(1, 3))])
        else:
            return ''

    def _create_frame(self, code):
        formatter = SvgFormatter(full = True,
                                 fontsize = '24px',
                                 linenos = True,
                                 style = self.style)
        return highlight(code, self.lexer, formatter)

    def animate_scene(self, scene_number):
        all_sequences = []
        if scene_number == 0:
            # animate base code
            image_sequence = []
            source_code = ''.join([seg['code'] for seg in self.code_segments
                                   if seg['class'] == 'text'])
            index_first = [seg['scene'] for seg in self.code_segments].index(0)
            typing_time = self.code_segments[index_first]['time'][0]
            pause_time = self.code_segments[index_first]['time'][1]
            typing_position = 0
            while typing_position < len(source_code):
                typing_position += self._typing_step()
                image_sequence.append(self._create_frame(
                    source_code[:typing_position + 1] + self._typo() +
                    '\u2588'))
            image_sequence.append(self._create_frame(source_code))
            all_sequences.append({
                'typing': typing_time,
                'pause': pause_time,
                'frames': image_sequence})

        else:
            segments = [seg for seg in self.code_segments if
                        seg['class'] == 'text' or seg['class'] == 'from' and
                        seg['scene'] <= scene_number or seg[
                            'class'] == 'only' and seg[
                            'scene'] == scene_number]
            animations_indexes = [idx for (idx, seg) in enumerate(segments)
                                  if seg['class'] != 'text' and
                                  seg['scene'] == scene_number]

            for animated_segment in animations_indexes:
                preceding_code = ''.join(
                    [seg['code'] for seg in segments[:animated_segment]])
                animated_code = segments[animated_segment]['code']
                following_code = ''.join(
                    [seg['code'] for seg in segments[animated_segment + 1:] if
                     seg['class'] == 'text' or
                     seg['class'] in ['from', 'only'] and
                     seg['scene'] < scene_number])

                image_sequence = []
                typing_position = 0
                while typing_position <= len(animated_code):
                    typing_position += self._typing_step()
                    image_sequence.append(self._create_frame(
                        preceding_code +
                        animated_code[:typing_position + 1] +
                        self._typo() + '\u2588' +
                        following_code))
                image_sequence.append(self._create_frame(
                    preceding_code + animated_code + following_code))
                all_sequences.append({
                    'typing': segments[animated_segment]['time'][0],
                    'pause': segments[animated_segment]['time'][1],
                    'frames': image_sequence})

                if segments[animated_segment]['class'] == 'only':
                    image_sequence = []
                    for deleting_position in range(
                            len(segments[animated_segment]['code']) - 1,
                            -1, -1):
                        image_sequence.append(self._create_frame(
                            preceding_code +
                            animated_code[:deleting_position] + '\u2588' +
                            following_code))
                    image_sequence.append(self._create_frame(
                        preceding_code + following_code))
                    all_sequences.append({
                        'typing': segments[animated_segment]['time'][2],
                        'pause': segments[animated_segment]['time'][3],
                        'frames': image_sequence})

        return all_sequences

    def animate(self, verbose = True):
        temp_prefix = f'/tmp/typing.tmp.{getpid()}_'
        ffmpeg_options = '-vf fps=30 -vcodec libx264 -b:v 20M -s 1280x720 '
        # scene_frames_count = []
        concatation = ''
        scene_frame_counter = 0  # for scene sequence in filenames
        for scene_counter in range(self.scene_counter + 1):
            if verbose:
                print(f'> Scene #{scene_counter}:\n  - Creating frames ',
                      end = '')
            animations = self.animate_scene(scene_counter)
            if verbose:
                if len(animations) == 0:
                    print('(empty)')
                else:
                    print(f'({len(animations)} animations)')
            for animation_counter, current_scene in enumerate(animations):
                if verbose:
                    print(f'  - Saving frames: ' +
                          f'{current_scene["typing"]}s/' +
                          f'{current_scene["pause"]}s')
                for count, frame in enumerate(current_scene['frames']):
                    filename = temp_prefix + \
                               f'{scene_frame_counter:02d}_' + \
                               f'{animation_counter:02d}_{count:03d}.svg'
                    open(filename, 'w').write(frame)

                if verbose:
                    print('\tCreating clip (animation) with ' +
                          f'{len(current_scene["frames"])} frames')
                frame_rate = \
                    len(current_scene['frames']) / current_scene['typing']
                filename = f'{temp_prefix}{scene_frame_counter:02d}' + \
                           f'_{animation_counter:02d}'
                # print('    - file:', filename)
                system('ffmpeg -nostdin ' +
                       f'-r {frame_rate:.5f} -f image2 -i ' +
                       temp_prefix + f'{scene_frame_counter:02d}_' +
                       f'{animation_counter:02d}_%3d.svg ' +
                       ffmpeg_options +
                       filename + '_anim.mp4'
                       + ' >> /tmp/log 2> /tmp/log'
                       )
                concatation += f"file '{filename}_anim.mp4'\n"

                if current_scene['pause'] != 0:
                    if verbose: print('\tCreating clip (pause)')
                    clip_filename = f'{temp_prefix}{scene_frame_counter:02d}' + \
                                    f'_{animation_counter:02d}_pause.mp4'
                    system('ffmpeg -nostdin -loop 1 -i ' +
                           temp_prefix +
                           f'{scene_frame_counter:02d}_{animation_counter:02d}' +
                           f'_{len(current_scene["frames"]) - 1:03d}.svg ' +
                           ffmpeg_options +
                           f' -t {current_scene["pause"]} ' + clip_filename
                           + ' >> /tmp/log 2> /tmp/log'
                           )
                    concatation += \
                        f"file '{temp_prefix}" + \
                        f"{scene_frame_counter:02d}_{animation_counter:02d}_pause.mp4'\n"
                scene_frame_counter += 1

        # final video
        if verbose:
            print('> Creating video')
            print('  - Creating config file')
        open(temp_prefix + 'concat.txt', 'w').write(concatation)
        if verbose: print('  - Concatenating clips', end = '')
        system('ffmpeg -nostdin -f concat -safe 0 -i ' + temp_prefix +
               f'concat.txt -c copy -y code_{getpid()}.mp4'
               + ' >> /tmp/log 2> /tmp/log'
               )
        if verbose: print('')

        # cleanup
        system(f'rm -f {temp_prefix}*')
