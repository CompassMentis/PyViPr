import argparse

from part import Part
from settings import Settings


def build(part_name):
    part = Part.from_file(part_name)

    part.build()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('part', const=Settings.default_part, nargs='?', default=Settings.default_part)

    args = parser.parse_args()

    build(args.part)


if __name__ == '__main__':
    main()
