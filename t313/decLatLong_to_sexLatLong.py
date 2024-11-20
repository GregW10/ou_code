#!/usr/bin/python3

import sys
import sup


def main():
    if len(sys.argv) < 2:
        print("Usage: ./convert <decimal_lat/long> ...", file=sys.stdout)
        sys.exit(1)
    for arg in sys.argv[1:]:
        degs, mins, secs = sup.dec_latlong_to_sex_latlong(float(arg))
        print(f"{arg} deg = {degs:.0f} deg {mins:.0f}' {secs:.5f}\"")


if __name__ == "__main__":
    main()
