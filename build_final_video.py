# TODO: Combine with build, specify what to build as an extra argument
import argparse

from part import Part
from settings import Settings


def build_final_video(part_name):
    part = Part.from_file(part_name)

    part.build()

    print('Putting it all together - combining videos')
    part.build_final_video()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('part', const=Settings.default_part, nargs='?', default=Settings.default_part)

    args = parser.parse_args()

    build_final_video(args.part)


if __name__ == '__main__':
    main()
