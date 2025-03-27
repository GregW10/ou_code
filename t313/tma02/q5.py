#!/usr/bin/env python3

import math
import sup
import sys
import os

diny = 365.25

blue = ""
bold = ""
reset = ""


def main():
    if os.isatty(sys.stdout.fileno()):
        blue = "\033[38;5;12m"
        bold = "\033[1m"
        reset = "\033[0m"
    print(f"{blue}######################################\n{bold}Question a{reset}")
    land_area = 8.7e9 # hectares (ha)
    prop = 0.1
    target_output = 200e18 # J/yr
    required_output = target_output/(prop*land_area) # J yr^-1 ha^-1
    print(f"Required output = {required_output/1e9} GJ yr^-1 ha^-1")





if __name__ == "__main__":
    main()

