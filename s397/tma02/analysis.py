#!/usr/bin/python3

import sys
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fname")
    parser.add_argument("-s", "--show", action="store_true")
    args = parser.parse_args()
    df = pd.read_csv(args.fname)
    qrobur = df.loc[[s.lower() == "quercus robur" for s in df["Species"].astype(str)]]
    print("Part 1 - Test for significant variation between Canopy Cover Indices in Quercus Robur trees with "
          "different urbanisation categories.")
    print(qrobur)





if __name__ == "__main__":
    main()
