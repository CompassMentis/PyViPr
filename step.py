import os
import time

import imgkit

from vo_line import VOLine
from settings import Settings
import file_operations
import create_html
import terminal
import create_source_code_image
import video_and_sound_operations
import recording


def line_numbers_from_command(remainder):
    """
    From 5, 7-10, 8
    To 5, 7, 8, 9, 10
    """
    parts = remainder.split(',')
    result = set()
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if '-' not in part:
            result.add(int(part))
            continue

        left, right = part.split('-')
        left, right = int(left), int(right)
        assert left <= right
        result = result | set(range(left, right + 1))
    return list(result)


def replace_show_and_run_lines(lines):
    result = []
    for line in lines:
        if not line.startswith('c_show_code_and_run'):
            result.append(line)
            continue

        filename = line.split(' ', 1)[1]

        if '¬' in filename:
            filename, duration = filename.split('¬')
            result.append(f'$python {filename} ¬ {duration}')
        else:
            result.append(f'$python {filename}')

        result.append(f'c_show_code {filename}')
    return result


def replace_lines_commands(lines, previous_lines):
    """
    Replace lines which start with c_lines with c_show_code <last file> ....
    """
    result = []
    filename = None
    for line in previous_lines:
        if line.startswith('c_show_code'):
            # filename = line.split(' ', 1)[1]
            _, filename, *remainder = line.split(' ')

    for line in lines:
        if line.startswith('c_show_code'):
            filename = line.split()[1]
        elif line.startswith('c_lines'):
            assert filename
            numbers = line.split(' ', 1)[1]
            line = f'c_show_code {filename} {numbers}'
        result.append(line)
    return result


def pre_process_step_lines(lines, previous_lines):
    # c_show_and_run --> c_show and >>>python
    # c_lines -> c_show <line numbers>
    # 5-10 with 5, 6, 7, 8, 9, 10
    # and maybe more
    lines = replace_show_and_run_lines(lines)
    lines = replace_lines_commands(lines, previous_lines)

    return lines


def get_raw_demo_name():
    for name in os.listdir(Settings.obs_recordings_path):
        if name.startswith('20'):
            return name


def strip_lines(lines):
    """
    remove empty string(s) at start and end of list of lines
    """
    return '\n'.join(lines).strip().split('\n')


class Step:
    def __init__(self, slide, lines):
        self.slide = slide
        self.raw_lines = lines
        self.comment_lines = []
        self.text_lines = []
        self.vo_lines = []
        self.python_lines = []
        self.terminal_lines = []
        self.command_lines = []
        self.timestamp = None
        self.id = None

    def save_needed(self, target):
        """
        If not previously saved, just save it
        If saved copy found,
            check time stamp.
            If newer than contents.txt, no need to save
            If older, read. If same as current content, no need to save
            Save if necessary
        """
        if not os.path.isfile(target):
            return True

        target_timestamp = os.path.getmtime(target)
        contents_timestamp = os.path.getmtime(self.path + '/contents.txt')

        if target_timestamp > contents_timestamp:
            return False

        with open(target) as input_file:
            old_version = input_file.read()

        return old_version != self.to_save()

    def init(self):
        """
        Called after step is created and any missing ids filled in

        If necessary, save

        Record timestamp of saved file
        """
        # Sanity check: Can't have both python and terminal demo on same step
        assert not self.python_lines or not self.terminal_lines

        target = self.save_target

        if self.save_needed(target):
            print(f'Saving {target}')
            with open(target, 'w') as output_file:
                output_file.write(self.to_save())

        self.timestamp = os.path.getmtime(target)

    def old_or_missing(self, target):
        if not os.path.isfile(target):
            return True

        target_timestamp = os.path.getmtime(target)
        return target_timestamp < self.timestamp

    @property
    def path(self):
        result = f'{Settings.root_path}{self.slide.part.name}/'
        file_operations.ensure_path(result)
        return result

    @property
    def build_folder(self):
        path = f'{self.path}build/'
        file_operations.ensure_path(path)
        return path

    @property
    def recordings_folder(self):
        return f'{self.path}recordings/'

    @property
    def save_target(self):
        return f'{self.build_folder}step_{self.id:05}.txt'

    @property
    def slide_content_target(self):
        if self.text_lines:
            return f'{self.build_folder}slide_content_{self.id:05}.png'

        result = None
        for step in self.slide.steps:
            if step == self:
                assert result
                return result
            if step.text_lines:
                result = step.slide_content_target

        assert False

    @property
    def demo_lines(self):
        return self.python_lines + self.terminal_lines

    @property
    def demo_target(self):
        return f'{self.build_folder}demo_{self.id:05}.mp4'

    @property
    def demo_video_target(self):
        return f'{self.build_folder}demo_{self.id:05}.mp4'

    @property
    def cropped_demo_video_target(self):
        return f'{self.build_folder}cropped_demo_{self.id:05}.mp4'

    @property
    def text_video_target(self):
        return f'{self.build_folder}text_video_{self.id:05}.mp4'

    @property
    def text_and_demo_video_target(self):
        return f'{self.build_folder}text_and_demo_{self.id:05}.mp4'

    @property
    def source_code_image_target(self):
        """
        If this step includes a source code - return that

        Otherwise, go through all previous steps,
        remember the source code image
        use the last one of these
        """
        if self.show_code_command:
            return f'{self.build_folder}source_code_{self.id:05}.png'

        result = None
        for step in self.slide.steps:
            if step == self:
                assert result
                return result
            if step.show_code_command:
                result = step.source_code_image_target

        assert False

    @property
    def show_video_command(self):
        for command in self.command_lines:
            if command.startswith('c_show_video'):
                return command

    @property
    def show_video_source(self):
        command = self.show_video_command
        name = command.split(' ', 1)[1]
        return f'{Settings.root_path}source_videos/{name}'

    @property
    def last_demo_frame_target(self):
        """
        If this step includes a demo - return the last frame of the demo

        Otherwise, go through all previous steps,
        for any demos, remember the last frame
        use the last one of these
        """

        if self.demo_lines:
            return f'{self.build_folder}last_demo_frame_{self.id:05}.png'

        result = None
        for step in self.slide.steps:
            if step == self:
                assert result
                return result
            if step.demo_lines:
                result = step.last_demo_frame_target

        return None

    @property
    def combined_voice_over_target(self):
        return f'{self.build_folder}combined_voice_over_{self.id:05}.wav'

    @property
    def final_image_target(self):
        return f'{self.build_folder}final_image{self.id:05}.png'

    @property
    def final_target(self):
        return f'{self.build_folder}final_{self.id:05}.mp4'

    def __str__(self):
        return f"""Slide, id={self.id}
text lines:
{'''
'''.join(self.text_lines)}

vo_lines:
{'''
'''.join(str(line) for line in self.vo_lines)}"""

    @staticmethod
    def from_lines(slide, lines):
        lines = [line.strip() for line in strip_lines(lines)]

        # Replace:
        # c_show_and_run --> c_show and >>>python
        # c_lines -> c_show <line numbers>
        # 5-10 with 5, 6, 7, 8, 9, 10
        # and maybe more

        previous_lines = []
        for step in slide.steps:
            previous_lines += step.command_lines

        lines = pre_process_step_lines(lines, previous_lines)

        result = Step(slide, lines)
        if lines[0].startswith('[step '):
            result.id = int(lines[0].split()[1].replace(']', ''))
            lines = lines[1:]
        else:
            result.id = None

        result.comment_lines = [line for line in lines if line.startswith('#')]
        result.text_lines = [line for line in lines if line.startswith('t_') or line.startswith('t ')]
        result.vo_lines = [VOLine.from_text(result, line[2:].strip()) for line in lines if line.startswith('vo ')]
        result.python_lines = [line[3:] for line in lines if line.startswith('>>>')]
        result.terminal_lines = [line[1:] for line in lines if line.startswith('$')]
        result.command_lines = [line for line in lines if line.startswith('c_')]
        if len(result.comment_lines + result.vo_lines + result.text_lines + result.python_lines +
                   result.terminal_lines + result.command_lines) != len(lines):
            print('Step incorrect')
            print('\n'.join(lines))
            raise BaseException

        return result

    def to_save(self):
        return f'[step {self.id}]\n' + \
               '\n'.join(
                   self.comment_lines +
                   self.text_lines +
                   self.command_lines +
                   [vo_line.to_text() for vo_line in self.vo_lines] +
                   [f'>>>{line}' for line in self.python_lines] +
                   [f'${line}' for line in self.terminal_lines]
               ) + '\n\n'

    def build_slide_needed(self):
        # No text lines, no need to create a slide for this step
        if not self.text_lines:
            return False

        # Is the target file missing or out of date?
        target = self.slide_content_target
        return self.old_or_missing(target)

    def build_slide(self):
        target = self.slide_content_target
        print(target)

        if self.slide.type == 'title':
            width, height = Settings.TitleSlide.text_size
        else:
            width, height = {
                1: Settings.OneColumnSlide.text_size,
                2: Settings.TwoColumnSlide.text_size,
            }[self.slide.slide_columns]

        html = create_html.slide_lines_to_html(self.slide.text_so_far)

        with open(f'{Settings.templates_path}{self.slide.type}_slide.html') as input_file:
            template = input_file.read()
        html = template.replace('{html}', html)

        # Detail slides have two different widths
        if self.slide.type == 'detail':
            html = html.replace('{width}', str(width)).replace('{height}', str(height))

        # wkhtmltoimage often raises an OSError
        # On the second try it usually works
        for _ in range(3):
            try:
                imgkit.from_string(
                    html,
                    target,
                    options={
                        'crop-w': str(width),
                        'crop-h': str(height),
                    }
                )
                break
            except OSError:
                pass

    def build_demo_needed(self):
        # No text lines, no need to create a slide for this step
        if not self.demo_lines:
            return False

        # Is the target file missing or out of date?
        target = self.demo_target
        return self.old_or_missing(target)

    def create_cropped_demo_video(self):
        if not self.demo_lines:
            return

        source = self.demo_video_target
        target = self.cropped_demo_video_target

        # Target already up to date - done
        if file_operations.already_up_to_date(source=source, target_file=target):
            return

        if self.slide.slide_columns == 1:
            target_size = Settings.OneColumnSlide.demo_size
        else:
            target_size = Settings.TwoColumnSlide.demo_size

        # Crop recording
        command = f'ffmpeg -y -i "{source}" ' \
                  f'-filter:v "crop={target_size[0]}:{target_size[1]}:0:0" "{target}"'
        print(command)
        os.system(command)

    def extract_last_demo_frame(self):
        if not self.demo_lines:
            return

        source = self.cropped_demo_video_target
        target = self.last_demo_frame_target

        if file_operations.already_up_to_date(source, target):
            return

        video_and_sound_operations.extract_last_frame(
            source=source,
            target=target
        )

    def create_derived_demo_artifacts(self):
        """
        Called when creating final video

        Once raw demo video has been created, from this derive:
        * Cropped video - size depends on number of columns (slide.slide_columns - 1 or 2)
        * (from cropped video) - extract last frame
            used for slides which follow a demo but which don't have their own demo
        """
        self.create_cropped_demo_video()
        self.extract_last_demo_frame()

    def build_demo(self):
        """
        At this point, 'slide' code already prepared the terminal
            right size, started python if necessary, cleared if necessary

        Just run the code
        """

        print(f'building {self.demo_video_target}')

        # Move any old recordings out of the way
        file_operations.ensure_path(f"{Settings.obs_recordings_path}obsolete/")
        os.system(f'mv "{Settings.obs_recordings_path}"20*.mp4 "{Settings.obs_recordings_path}obsolete/"')

        # Start recording
        # Click on python window first - otherwise cursor is over recording button, so can't be found
        terminal.press_button('terminal', ignore_not_found=True)
        terminal.press_button('start_recording_button')

        # Select the shell
        terminal.press_button('terminal')

        # Run the code
        terminal.run_python_code(self.python_lines + self.terminal_lines, character_delay=0.1, line_delay=0.5)

        # Stop recording - even though start button no longer visible
        # we've cached its location
        # It has been replaced by the stop button, so this will stop the recording
        terminal.press_button('start_recording_button')
        # terminal.press_button('stop_recording_button')

        # Wait for OBS to save the recording
        time.sleep(2)

        # Rename the recording and move to the target location
        raw_demo_name = get_raw_demo_name()
        assert raw_demo_name is not None

        target = self.demo_video_target
        command = f'mv "{Settings.obs_recordings_path}{raw_demo_name}" "{target}"'
        print(command)
        os.system(command)

    def contains_clear_demo_command(self):
        for command in self.command_lines:
            if command == 'c_clear_demo':
                return True
        return False

    @property
    def show_code_command(self):
        commands = [command for command in self.command_lines if command.startswith('c_show_code')]
        if not commands:
            return None

        # Can show a maximum of 1 source code per step
        assert len(commands) == 1

        return commands[0]

    def build_code_image(self):
        command = self.show_code_command
        if not command:
            return

        # c_show_code <filename> 5, 10, 3
        # c_show_code <filename>

        _, filename, *remainder = command.split()
        source = Settings.source_code_path  + filename

        highlighted = line_numbers_from_command(' '.join(remainder))

        target = self.source_code_image_target

        if file_operations.already_up_to_date(source, target):
            return

        create_source_code_image.create_source_code_image(
            source_file_name=source,
            target_file_name=target,
            highlighted=highlighted
        )

    def combine_voice_overs(self):
        """
        Combine the voice over recordings into a single recording for this step
        """
        # No voice over lines - done
        if not self.vo_lines:
            return

        # Already up to date - done
        source_files = [self.recordings_folder + vo_line.final_audio_recording_name for vo_line in self.vo_lines]
        if file_operations.already_up_to_date(source_files, self.combined_voice_over_target):
            return

        video_and_sound_operations.combine_audio_sequentially(sources=source_files, target=self.combined_voice_over_target)

    @property
    def hide_demo_command(self):
        return 'c_hide_demo' in self.command_lines

    @property
    def hide_code_command(self):
        return 'c_hide_code' in self.command_lines

    @property
    def shows_demo(self):
        if self.demo_lines:
            return True

        result = False
        for step in self.slide.steps:
            if step.demo_lines:
                result = True
            elif step.hide_demo_command:
                result = False

            if step == self:
                return result

        assert False

    @property
    def shows_code(self):
        if self.show_code_command:
            return True

        result = False
        for step in self.slide.steps:
            if step.show_code_command:
                result = True
            elif step.hide_code_command:
                result = False
            elif step.image_command_line:
                result = False

            if step == self:
                return result

        assert False

    @property
    def shows_text(self):
        if self.text_lines:
            return True

        result = False
        for step in self.slide.steps:
            if step == self:
                return result

            if step.text_lines:
                result = True

        assert False

    @property
    def image_command_line(self):
        for command in self.command_lines:
            if command.startswith('c_show_image'):
                return command

    @property
    def shows_image(self):
        # If this step or a previous step has an image, return True

        # TODO: Handle image being replaced by demo
        # TODO: Handle image in a two column slide
        if self.image_command_line:
            return True

        result = False

        for step in self.slide.steps:
            if step.image_command_line:
                result = True

            if step.demo_lines:
                result = False

            if step.show_code_command:
                result = False

            if step == self:
                return result

    @property
    def image_source(self):
        if self.image_command_line:
            return f"{Settings.images_path}{self.image_command_line.split(' ', 1)[1]}"

        result = None
        for step in self.slide.steps:
            if step == self:
                return result

            if not step.image_command_line:
                continue

            result = step.image_source

    def create_final_image(self):
        """
        Combine following:
            Background image - based on slide.type
            Demo shadow image - none, one column, two columns
            Last frame - if no demo lines on this slide, but demo still active
            Code shadow image - if code showing
            Code image - if code showing
        """
        # TODO: Only do this if necessary?

        to_combine = []
        columns = self.slide.slide_columns

        # Background image
        if self.slide.type == 'title':
            to_combine.append(
                (Settings.title_background, (0, 0), None)
            )
        else:
            to_combine.append(
                (Settings.detail_background, (0, 0), None)
            )

        # Demo background plus, if necessary, last frame from previous step
        if self.shows_demo:
            if columns == 1:
                to_combine.append(
                    (Settings.one_column_demo_background, (0, 0), None)
                )
            else:
                to_combine.append(
                    (Settings.two_column_demo_background, (0, 0), None)
                )

            # Shows demo, but no video for this step
            if not self.demo_lines:
                if columns == 1:
                    to_combine.append(
                        (
                            self.last_demo_frame_target,
                            Settings.OneColumnSlide.last_demo_frame_location,
                            Settings.OneColumnSlide.demo_size
                        )
                    )
                else:
                    to_combine.append(
                        (
                            self.last_demo_frame_target,
                            Settings.TwoColumnSlide.last_demo_frame_location,
                            Settings.TwoColumnSlide.demo_size
                        )
                    )

        if self.shows_code:
            if self.shows_text:
                to_combine.append(
                    (
                        self.slide_content_target,
                        Settings.TwoColumnSlide.text_location,
                        Settings.TwoColumnSlide.title_only_size
                    )
                )

            to_combine.append(
                (Settings.two_column_code_background, (0, 0), None)
            )

            to_combine.append(
                (
                    self.source_code_image_target,
                    Settings.TwoColumnSlide.code_location,
                    Settings.TwoColumnSlide.code_size
                )
            )

        elif self.shows_text:
            if self.slide.type == 'title':
                to_combine.append(
                    (
                        self.slide_content_target,
                        Settings.TitleSlide.text_location,
                        Settings.TitleSlide.text_size
                    )
                )
            elif columns == 1:
                if self.shows_demo:
                    to_combine.append(
                        (
                            self.slide_content_target,
                            Settings.OneColumnSlide.text_location,
                            Settings.OneColumnSlide.title_only_size
                        )
                    )
                else:
                    to_combine.append(
                        (
                            self.slide_content_target,
                            Settings.OneColumnSlide.text_location,
                            Settings.OneColumnSlide.text_size
                        )
                    )
            else:
                to_combine.append(
                    (
                        self.slide_content_target,
                        Settings.TwoColumnSlide.text_location,
                        Settings.TwoColumnSlide.text_size
                    )
                )

        if self.shows_image:
            to_combine.append(
                (
                    self.image_source,
                    Settings.OneColumnSlide.demo_location,
                    Settings.OneColumnSlide.demo_size
                )
            )

        target = self.final_image_target
        if file_operations.already_up_to_date([source for source, _, _ in to_combine], target):
            return

        video_and_sound_operations.combine_images(to_combine, target)

    @property
    def target_duration(self):
        """
        Return maximum of following:
            if voice over - combined voice over duration
            if demo - demo duration
            Settings.minimum_step_duration
        """
        durations = [Settings.minimum_step_duration]
        if self.vo_lines:
            voice_over_duration = recording.get_audio_recording_duration(self.combined_voice_over_target)
            minutes, seconds = voice_over_duration.split(':')
            minutes, seconds = int(minutes), int(seconds)
            durations.append(60 * minutes + seconds)

        if self.demo_lines:
            durations.append(
                video_and_sound_operations.get_video_length(self.cropped_demo_video_target)
            )

        result = max(durations)

        if self.start_of_slide:
            result += Settings.start_of_slide_delay

        if self.end_of_slide:
            result += Settings.end_of_slide_delay

        return result

    @property
    def start_of_slide(self):
        return self.slide.steps[0] == self

    @property
    def end_of_slide(self):
        return self.slide.steps[-1] == self

    def generate_text_video(self):
        print('Step, generate_text_video')

        source = self.final_image_target
        target = self.text_video_target

        if file_operations.already_up_to_date(source, target):
            return

        duration = self.target_duration

        video_and_sound_operations.image_to_video(source, duration, target)

    def generate_text_and_demo_video(self):
        """
        Put the demo video on top of the text video
        """

        target = self.text_and_demo_video_target
        text_video_source = self.text_video_target

        if self.demo_lines:
            # Has some demo - merge into the text video
            demo_video_source = self.cropped_demo_video_target
        elif self.show_video_command:
            # Has a pre-recorded video to show - merge into the text video
            demo_video_source = self.show_video_source
        else:
            # No demo to merge into this - just copy
            if file_operations.already_up_to_date(text_video_source, target):
                return

            command = f'cp "{text_video_source}" "{target}"'
            print(command)
            os.system(command)
            return

        if file_operations.already_up_to_date([text_video_source, demo_video_source], target):
            return

        if self.slide.slide_columns == 1:
            location = Settings.OneColumnSlide.demo_location
        else:
            location = Settings.TwoColumnSlide.demo_location

        video_and_sound_operations.paste_video_unto_another(
            background_source=text_video_source,
            foreground_source=demo_video_source,
            foreground_location=location,
            target=target,
            starting_delay=Settings.start_of_slide_delay if self.start_of_slide else 0
        )

    def create_final_video(self):
        video_source = self.text_and_demo_video_target
        target = self.final_target

        if not self.vo_lines:
            if file_operations.already_up_to_date(video_source, target):
                return

            video_and_sound_operations.add_silent_audio_to_video(video_source, target)
            return

        audio_source = self.combined_voice_over_target
        if file_operations.already_up_to_date((video_source, audio_source), target):
            return

        video_and_sound_operations.combine_audio_and_video(
            audio_source=audio_source,
            video_source=video_source,
            target=target,
            starting_delay=Settings.start_of_slide_delay if self.start_of_slide else 0
        )

    def build_step_video(self):
        """
        Combines all the parts into a single video
        * Correct background image (title_slide_background.png or detail_slide_background.png)
            based on slide.type
        * Text
            build/slide_content_<step_id>.png
                or build/slide_title_<step_id>.png
            in location (todo)
            Only show title line if there is a python source code image on this step
                otherwise, show full slide
        * Python demo video
        * Terminal demo video
            Crop from
                build/demo_<step_id>.mp4, to
                build/cropped_demo_<step_id>.mp4
                On step it appears in
                (to size todo)
            Last frame of demo (above) on subsequent steps
                till step which contains a c_hide_demo command
            right column if python source code and/or text (other than title) on any step for this slide
                full-width (left column) otherwise
        * Python source code image
            from first step it appears in
            till step which contains a c_hide_code command
        * Voice over
            for each vo_line in step.vo_lines
                <vo_line.final_audio_recording_name>

        Overall duration:
            longest of
                sum(voice overs)
                demo video

        """
        self.create_derived_demo_artifacts()
        self.combine_voice_overs()
        self.create_final_image()
        self.generate_text_video()
        self.generate_text_and_demo_video()
        self.create_final_video()
