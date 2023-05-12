# TODO: It looks like this isn't used (any more). Delete after production of next (6th) video, or re-instate if needed after all
# import os
#
# from settings import Settings
# import file_operations
# import video_and_sound_operations
# from part import Part
#
#
# def extract_final_step_frames(part, target_folder):
#     file_operations.ensure_path(target_folder)
#     id = 1
#     for slide in part.slides:
#         for step in slide.steps:
#             source_file = step.final_target
#
#             if not os.path.isfile(source_file):
#                 continue
#
#             target_file = f'{target_folder}slide_{id:05}.png'
#             video_and_sound_operations.extract_last_frame(source_file, target_file)
#             id += 1
#
#
# def extract_final_slide_frames(part, target_folder):
#     file_operations.ensure_path(target_folder)
#     id = 1
#     for slide in part.slides:
#         source_file = slide.steps[-1].final_target
#
#         if not os.path.isfile(source_file):
#             continue
#
#         target_file = f'{target_folder}{part.name}_{id:05}.png'
#         video_and_sound_operations.extract_last_frame(source_file, target_file)
#         id += 1
#
#
# for name in os.listdir(Settings.root_path):
#     source_folder = Settings.root_path + name + '/'
#     if not os.path.isfile(source_folder + 'contents.txt'):
#         continue
#     source_folder += 'build/'
#     if not os.path.isdir(source_folder):
#         continue
#
#     part = Part.from_file(name)
#
#     extract_final_step_frames(part, Settings.root_path + 'final_step_images/' + name + '/')
#     extract_final_slide_frames(part, Settings.root_path + 'final_slide_images/')
