#!/usr/bin/python3

import sys
import json
import pandas as pd
from analysis import encoder


def main():
    if len(sys.argv) != 5:
        sys.exit(1)
    idx1 = int(sys.argv[1])
    idx2 = int(sys.argv[2])
    df1 = pd.read_csv(sys.argv[3])
    df2 = pd.read_csv(sys.argv[4])
    res1 = {"data-point": {}}
    res2 = {"data-point": {}}
    for label in ["Latitude", "Longitude", "Altitude", "Tree diameter (cm)", "Urbanisation index", "Stand density index", "Canopy index", "Phenological index"]:
        for idx, res, df in [(idx1, res1, df1), (idx2, res2, df2)]:
            res["data-point"][label] = df[label][idx]
    with open("idx1.json", "w") as f:
        json.dump(res1, f, indent=4, cls=encoder)
    with open("idx2.json", "w") as f:
        json.dump(res2, f, indent=4, cls=encoder)
            


if __name__ == "__main__":
    main()

