#/usr/bin/env python3
# coding: utf-8
'''
Standalone program to convert a kmz file into a svg
'''
import argparse

import kmz2svg

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("kmz", help="the kmz input file")
    parser.add_argument("svg", help="the svg output file")
    args = parser.parse_args()

    if not kmz2svg.is_valid_kmz(args.kmz):
        parser.error("The provided kmz input file is not valid")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    kmz2svg.convert(args.kmz, args.svg)
