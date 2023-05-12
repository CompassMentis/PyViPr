# TODO: Document this

from settings import Settings
import file_operations
import video_and_sound_operations
from part import Part

file_operations.ensure_path(Settings.slide_deck_path)
with open('projects/live_project.txt') as input_file:
    project = input_file.readline().strip()
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
        slide_number += 1
