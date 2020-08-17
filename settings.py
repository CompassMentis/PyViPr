LAST_FRAME_OFFSET = 1


class Settings:
    lines = [line.strip() for line in open('projects/live_project.txt')]
    root_path = lines[-1]
    default_part = next(part[1:].strip() for part in lines if part.startswith('*'))
    home_path = '/home/coen/DevRoot/pyViPr/'
    templates_path = f'{home_path}templates/'
    static_path = f'{root_path}static/'
    final_videos_path = f'{root_path}final/'
    production_videos_path = f'{root_path}production/'
    obs_recordings_path = root_path + 'OBS recordings/'
    images_path = f'{root_path}source_images/'

    # Each step should take at least .. seconds, even if no voice over or demo
    minimum_step_duration = 2

    temp_folder = root_path + 'temp/'
    build_folder = root_path + 'build/'
    source_code_path = '/home/coen/demos/'

    target_size = 1280, 720

    start_of_slide_delay = 2
    end_of_slide_delay = 2

    class TitleSlide:
        text_location = 440, 165
        text_size = 800, 425

    class OneColumnSlide:
        text_location = 23, 4
        text_size = 1207, 636
        title_only_size = 1207, 100

        demo_location = 35, 125
        # Not sure why, but by default the final frame gets offset a little, cause a jump in the video
        last_demo_frame_location = demo_location[0] - LAST_FRAME_OFFSET, demo_location[1] - LAST_FRAME_OFFSET
        # demo_location = 30, 120
        demo_size = 965, 555

        terminal_window = 120, 32

    class TwoColumnSlide:
        text_location = 23, 4
        text_size = 702, 676
        title_only_size = 1207, 100

        demo_location = 745, 45
        # Not sure why, but by default the final frame gets offset a little, cause a jump in the video
        last_demo_frame_location = demo_location[0] - LAST_FRAME_OFFSET, demo_location[1] - LAST_FRAME_OFFSET
        demo_size = 485, 585

        code_location = 30, 120
        code_size = 695, 560

        # terminal_window = 40, 25
        terminal_window = 59, 34

    title_background = f'{templates_path}title_slide_background.png'
    detail_background = f'{templates_path}detail_slide_background.png'
    one_column_demo_background = f'{templates_path}one_column_demo_shadow.png'
    two_column_demo_background = f'{templates_path}two_column_demo_shadow.png'
    two_column_code_background = f'{templates_path}two_column_code_shadow.png'
