import os
import subprocess

from PIL import Image


def extract_last_frame(source, target):
    command = f"""ffmpeg -y -sseof -1 -i "{source}" -update 1 -q:v 1 "{target}" """
    print(command)
    os.system(command)


def combine_audio_sequentially(sources, target):
    source_list = ' '.join([f'-i "{source}"' for source in sources])
    command = f"""ffmpeg -y {source_list} -filter_complex 'concat=n={len(sources)}:v=0:a=1' "{target}" """
    print(command)
    os.system(command)


def combine_images(sources, target):
    image = Image.open(sources[0][0])
    for source_file, location, size in sources[1:]:
        next_image = Image.open(source_file)
        if size:
            width = min(size[0], next_image.width)
            height = min(size[1], next_image.height)
            next_image = next_image.crop((0, 0, width, height))
            image.paste(next_image, location)
        else:
            image.alpha_composite(next_image, location)
    image.save(target)


def get_video_length(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)


def image_to_video(source, duration, target):
    command = f'ffmpeg -y -loop 1 -i "{source}" -t {duration} -pix_fmt yuv420p "{target}"'
    print(command)
    os.system(command)


def paste_video_unto_another(background_source, foreground_source, foreground_location, target, starting_delay):
    # delay foreground source with <starting_delay> seconds
    command = f'ffmpeg -y ' \
              f'-i "{background_source}" ' \
              f'-itsoffset {starting_delay} -i "{foreground_source}" ' \
              f'-filter_complex "[0:v][1:v] overlay={foreground_location[0]}:{foreground_location[1]}" ' \
              f'-pix_fmt yuv420p ' \
              f'"{target}" '
    print(command)
    os.system(command)


def combine_audio_and_video(audio_source, video_source, target, starting_delay):
    # Delay audio source with <starting_delay> seconds

    # From https://linuxpip.org/ffmpeg-combine-audio-video/
    # -map 0:v:0 means that select the first input file (INPUT_FILE.mp4), then select the first (0) video stream. The first number (0) is the index of the first input file, the latter is the index number of the video stream.
    command = f'ffmpeg -y -itsoffset {starting_delay} -i "{audio_source}" -i "{video_source}" -c:v copy -c:a aac -map 1:v:0 -map 0:a:0 -strict experimental "{target}"'
    print(command)
    os.system(command)


def combine_videos(sources, target):
    # From https://trac.ffmpeg.org/wiki/Concatenate
    source_list = ' '.join([f'-i "{source}"' for source in sources])
    source_list = source_list
    command = f"""ffmpeg -y {source_list} -filter_complex 'concat=n={len(sources)}:v=1:a=1' "{target}" """
    print(command)
    os.system(command)


def add_silent_audio_to_video(source, target):
    command = f'ffmpeg -y -i "{source}" -f lavfi -i anullsrc -c:v copy -c:a aac -shortest "{target}"'
    print(command)
    os.system(command)
