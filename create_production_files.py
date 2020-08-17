"""
    • Script to create production videos
        ◦ Copy to ‘production’ folder
        ◦ Renumber final videos so start with 1, not 0
            ▪ Sample names:
                • 89081128_Groot_ Part2.mp4
                • 89081128_Groot_ Part2Segment1.mp4

    From: part1_1_threads
"""

import os

from settings import Settings
import file_operations

file_operations.ensure_path(Settings.production_videos_path)
lines = [line.strip().replace('*', '') for line in open('projects/live_project.txt') if line.strip()]
prefix = lines[-2]
assert prefix.startswith('prefix:')
prefix = prefix.split(' ', 1)[1].strip()

for part_name in lines[:-2]:
    source_name = f'{Settings.final_videos_path}{part_name}.mp4'
    assert os.path.isfile(source_name)

    parts = part_name.split('_')
    assert parts[0].startswith('part')
    part_number = int(parts[0][4:]) + 1
    target_name = f'{prefix}Part{part_number}'
    segment_number = int(parts[1])
    if segment_number:
        target_name += f'Segment{segment_number}'
    target_name += '.mp4'

    command = f'cp "{source_name}" "{Settings.production_videos_path}{target_name}"'
    print(command)
    os.system(command)
