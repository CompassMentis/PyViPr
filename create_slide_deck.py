import os

from settings import Settings
import file_operations
import video_and_sound_operations
from part import Part

file_operations.ensure_path(Settings.slide_deck_path)
with open('projects/live_project.txt') as input_file:
    project = input_file.readline().strip()
# lines = [line.strip() for line in open(f'projects/{project}')]
lines = [line.strip().replace('*', '') for line in open(f'projects/{project}') if line.strip()]
lines = lines[:-2]

slide_number = 1
for part_name in lines:
    part = Part.from_file(part_name)
    for slide in part.slides:
        last_step = slide.steps[-1]
        source = last_step.final_target
        target = f'{Settings.slide_deck_path}slide_{slide_number:004}.png'
        video_and_sound_operations.extract_last_frame(source, target)
        # if slide_number > 5:
        #     assert False
        #
        #
        # command = f'cp "{source}" "{target}"'
        # print(command)
        # os.system(command)
        slide_number += 1
    #
    # source_name = f'{Settings.final_videos_path}{part_name}.mp4'
    # assert os.path.isfile(source_name)
    #
    # parts = part_name.split('_')
    # assert parts[0].startswith('part')
    # part_number = int(parts[0][4:]) + 1
    # target_name = f'{prefix}Part{part_number}'
    # segment_number = int(parts[1])
    # if segment_number:
    #     target_name += f'Segment{segment_number}'
    # target_name += '.mp4'
    #
    # command = f'cp "{source_name}" "{Settings.production_videos_path}{target_name}"'
    # print(command)
    # os.system(command)
