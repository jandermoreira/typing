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
from pygments.formatters.svg import SvgFormatter  
from pygments.styles import get_style_by_name


class TypingNoTimeline(Exception):
    '''No timeline'''


class TypingUnbalancedMarkup(Exception):
    '''Unbalanced markup tags'''


class Typing:
    def __init__(self, source_code = '', language = 'C', style = 'default'):
        self.scene_counter = 0
        self.language = language
        self.source_code = source_code
        self.code_segments = self.segment_code(source_code)
        self.style = style

    def segment_code(self, source_code):
        source_code = source_code.replace('\n', '@newline@')

        # Get base times
        match_result = re.search(r'@base: \((.*?)\)@', source_code)
        if not match_result:
            base_time = [3., 0.]
        else:
            base_time = [float(t) for t in match_result.group(1).split(',')]
            source_code = source_code.replace(match_result.group(0), '')

        # Get code segments
        match_result = True
        code_segments = []
        while match_result:
            match_result = re.search(
                r'@(from|only):(\d)[\s]*\((.*?)\)>(.*?)<(from|only)@',
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

    def animate_scene(self, scene_number):
        print(f'> Animating scene #{scene_number}')
        lexer = lexers.get_lexer_by_name(self.language)

        all_sequences = []

        image_sequence = []
        if scene_number == 0:
            # animate base code
            # print(']]]]] base code')
            source_code = ''.join([seg['code'] for seg in self.code_segments
                                   if seg['class'] == 'text'])
            index_first = [seg['scene'] for seg in self.code_segments].index(0)
            typing_time = self.code_segments[index_first]['time'][0]
            pause_time = self.code_segments[index_first]['time'][1]
            typing_position = 0
            while typing_position < len(source_code):
                typing_position += self._typing_step()
                formatter = SvgFormatter(full = True,
                                           style = get_style_by_name(
                                               self.style))
                image_sequence.append(
                    highlight(source_code[:typing_position + 1] + '\u2588',
                              lexer, formatter))
            formatter = SvgFormatter(full = True,
                                       style = get_style_by_name(
                                           self.style))
            image_sequence.append(highlight(source_code, lexer, formatter))
            all_sequences.append({
                'typing': typing_time,
                'pause': pause_time,
                'frames': image_sequence})
            # print(source_code)

        else:
            segments = [seg for seg in self.code_segments if
                        seg['class'] == 'text' or seg['class'] == 'from' and
                        seg['scene'] <= scene_number or seg[
                            'class'] == 'only' and seg['scene'] == scene_number]
            # for s in segments:
            #     print('   >', s)
            animations_indexes = [idx for (idx, seg) in enumerate(segments) if
                                  seg['class'] != 'text' and
                                  seg['scene'] == scene_number]
            # print(']]]', animations_counter, 'animations in this scene:',
            #       animations_indexes)

            for animated_segment in animations_indexes:
                print('>>> typing', segments[animated_segment],
                      '\n>>>>>>>>>>>>>>>>>>>>>\n')
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
                    formatter = SvgFormatter(full = True,
                                               style = get_style_by_name(
                                                   self.style))
                    image_sequence.append(highlight(
                        preceding_code +
                        animated_code[:typing_position + 1] + 'X\u2588' +
                        following_code, lexer, formatter))
                all_sequences.append({
                    'typing': segments[animated_segment]['time'][0],
                    'pause': segments[animated_segment]['time'][1],
                    'frames': image_sequence})

                if segments[animated_segment]['class'] == 'only':
                    # print('>>>>>>>>>> deleting', segments[animated_segment])
                    image_sequence = []
                    for deleting_position in range(
                            len(segments[animated_segment]['code']) - 1, 0,
                            -1):
                        formatter = SvgFormatter(
                            full = True, style = get_style_by_name(self.style))
                        # print('::::::::', animated_code[:deleting_position])
                        image_sequence.append(highlight(
                            preceding_code +
                            animated_code[:deleting_position] + 'A\u2588' +
                            following_code, lexer, formatter))
                        print('--------------------------------------')
                        print('::::::::', animated_code[:deleting_position])
                        print('--------------------------------------')
                    all_sequences.append({
                        'typing': segments[animated_segment]['time'][2],
                        'pause': segments[animated_segment]['time'][3],
                        'frames': image_sequence})

                # print('---------------- antes\n', preceding_code)
                # print('---------------- animado\n', animated_code)
                # print('---------------- depois\n', following_code)

                formatter = SvgFormatter(full = True,
                                           style = get_style_by_name(
                                               self.style))
                image_sequence.append(highlight(
                    preceding_code + animated_code + following_code,
                    lexer, formatter))
        # print(f'>>>> {len(all_sequences)} sequences')
        # for s in all_sequences:
        #     print(f'({s[0]}, {s[1]}, ...)')
        return all_sequences

    def animate(self, verbose = True):
        temp_prefix = f'/tmp/typing.tmp.{getpid()}_'
        # scene_frames_count = []
        concatation = ''
        for scene_counter in range(self.scene_counter + 1):
            if verbose:
                print(f'> Scene #{scene_counter}:\n  - Creating frames ',
                      end = '')
            animations = self.animate_scene(scene_counter)
            if verbose: print(':', len(animations), 'animation(s)', end = '')
            for animation_counter, current_scene in enumerate(animations):
                if verbose:
                    print('\n  - Saving frames: ', current_scene['typing'],
                          current_scene['pause'])
                for count, frame in enumerate(current_scene['frames']):
                    filename = temp_prefix + \
                               f'{scene_counter:02d}_' + \
                               f'{animation_counter:02d}_{count:03d}.svg'
                    if verbose: print(f'\tFrame {count:03d}', filename)
                    open(filename, 'w').write(frame)

                if verbose:
                    print('\tCreating clip (animation) with ' +
                          f'{len(current_scene["frames"])} frames')
                frame_rate = \
                    len(current_scene['frames']) / current_scene['typing']
                filename = f'{temp_prefix}{scene_counter:02d}' + \
                           f'_{animation_counter:02d}'
                # print('    - file:', filename)
                system('ffmpeg -nostdin ' +
                       f'-r {frame_rate:.5f} -f image2 -i ' +
                       temp_prefix + f'{scene_counter:02d}_' +
                       f'{animation_counter:02d}_%3d.svg' +
                       ' -vf fps=30' +
                       f' -vcodec libx264 -b 800k -s 1280x720 ' +
                       filename + '_anim.mp4'
                       + ' >> /tmp/log 2> /dev/null'
                       )
                concatation += f"file '{filename}'_anim.mp4\n"

                if current_scene['pause'] != 0:
                    if verbose: print('\tCreating clip (pause)')
                    system('ffmpeg -nostdin -loop 1 -i ' +
                           temp_prefix +
                           f'{scene_counter:02d}_{animation_counter:02d}' +
                           f'_{len(current_scene["frames"]) - 1:03d}.svg' +
                           ' -vf fps=30' +
                           f' -vcodec libx264 -t {current_scene["pause"]}' +
                           ' -b 800k -s 1280x720' +
                           f' {temp_prefix}{scene_counter:02d}' +
                           f'_{animation_counter:02d}_pause.mp4'
                           + ' >> /tmp/log 2> /dev/null'
                           )
                    concatation += \
                        f"file '{temp_prefix}" + \
                        f"{scene_counter:02d}_{animation_counter:02d}_pause.mp4'\n"
                if verbose: print("< ")

        # final video
        if verbose:
            print('> Creating video')
            print('  - Creating config file')
        open(temp_prefix + 'concat.txt', 'w').write(concatation)
        if verbose: print('  - Concatenating clips', end = '')
        system('ffmpeg -nostdin -f concat -safe 0 -i ' + temp_prefix +
               f'concat.txt -c copy -y code_{getpid()}.mp4'
               +' > /tmp/log 2> /dev/null'
               )
        if verbose: print('\n<')

        # cleanup
        # system(f'rm -f {temp_prefix}*')


def main():
    source_code = open('samples/outro.c', 'r').read()
    try:
        segments = Typing(source_code)
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
        segments.animate()
        # segments.animate_scene(3)


if __name__ == '__main__':
    main()
