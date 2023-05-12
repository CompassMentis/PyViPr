# TODO: Combine with build, specify what to build as an extra argument
import argparse

from part import Part
from settings import Settings


def build_code_images(part_name):
    part = Part.from_file(part_name)

    part.build_code_images()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('part', const=Settings.default_part, nargs='?', default=Settings.default_part)

    args = parser.parse_args()

    build_code_images(args.part)


if __name__ == '__main__':
    main()
