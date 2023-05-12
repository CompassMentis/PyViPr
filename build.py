"""
Build a specified part or the default part
- Slides
- Record code demos
- Turn source code into syntax highlighted images
- Combine all the parts into a single video, one small video per step

Note: Does not combine the step videos into a part video

Syntax: python build.py [part-name]

The default part is set in Settings.default_part
"""
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
