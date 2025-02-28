#!/usr/bin/env python3

import fractions as frac


def main():
    size_covered = 440 # microns
    pixels_covered = 37*50
    pixel_size = frac.Fraction(numerator=440, denominator=pixels_covered)/1_000_000 # pixel size in metres
    print(pixel_size)


if __name__ == "__main__":
    main()
