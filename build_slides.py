# TODO: Combine with build, specify what to build as an extra argument
import argparse

from part import Part
from settings import Settings


def build_slides(part_name):
    part = Part.from_file(part_name)

    part.build_slides()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('part', const=Settings.default_part, nargs='?', default=Settings.default_part)

    args = parser.parse_args()

    build_slides(args.part)


if __name__ == '__main__':
    main()
