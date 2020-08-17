from settings import Settings
from slide import Slide
import file_operations
import video_and_sound_operations


def fill_in_missing_ids(part):
    ids = []
    for slide in part.slides:
        for step in slide.steps:
            ids.append(step.id)
            ids += [vo_line.id for vo_line in step.vo_lines]

    ids = [id for id in ids if id]

    next_id = max(ids) + 1 if ids else 1

    for slide in part.slides:
        for step in slide.steps:
            if not step.id:
                step.id = next_id
                next_id += 1

            for vo_line in step.vo_lines:
                if not vo_line.id:
                    vo_line.id = next_id
                    next_id += 1


def break_lines_into_slides(lines):
    """
    Each slide starts with a line starting with [slide:

    returns a list of list of lines - with each list of lines defining one slide
    """
    result = []
    slide_lines = []

    for line in lines:
        line = line.rstrip()
        if line.startswith('[slide'):
            if slide_lines:
                result.append(slide_lines)
            slide_lines = []
        slide_lines.append(line)

    if slide_lines:
        result.append(slide_lines)

    return result


class Part:
    def __init__(self, name):
        self.name = name
        self.slides = []
        self.raw_lines = []

        self._next_id = 0

    @property
    def next_id(self):
        result = self._next_id
        self._next_id += 1
        return result

    def record_id(self, id):
        if id >= self._next_id:
            self._next_id = id + 1

    @property
    def path(self):
        return f'{Settings.root_path}{self.name}/'

    @property
    def source_name(self):
        return f'{self.path}contents.txt'

    @property
    def final_video_target(self):
        file_operations.ensure_path(Settings.final_videos_path)
        return f'{Settings.final_videos_path}{self.name}.mp4'

    @staticmethod
    def from_file(name):
        result = Part(name)

        with open(result.source_name) as input_file:
            lines = input_file.readlines()

        result.raw_lines = lines
        result.slides = [Slide.from_text(result, slide_lines) for slide_lines in break_lines_into_slides(lines)]

        fill_in_missing_ids(result)

        result.save()

        for slide in result.slides:
            for step in slide.steps:
                step.init()

        return result

    def save(self):
        to_save = ''
        for slide in self.slides:
            to_save += slide.to_save()
        to_save = to_save.strip()

        if to_save == (''.join(self.raw_lines)).strip():
            # Nothing changed - done
            print('No changes')
            return

        file_operations.backup_file(self.source_name)

        with open(self.source_name, 'w') as output_file:
            output_file.write(to_save)
        print('New version created')

    def build_slides(self):
        for slide in self.slides:
            slide.build_slides()

    def build_demos(self):
        for slide in self.slides:
            print(f'Building demo {slide.id}')
            slide.build_demos()

    def build_code_images(self):
        for slide in self.slides:
            slide.build_code_images()

    def build(self):
        for slide in self.slides:
            slide.build_step_videos()

    def build_final_video(self):
        sources = [step.final_target for slide in self.slides for step in slide.steps]
        target = self.final_video_target
        if file_operations.already_up_to_date(sources, target):
            return

        video_and_sound_operations.combine_videos(sources, target)
