#!/usr/bin/python3

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from analysis import encoder


def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{gensymb}\\usepackage{siunitx}"
    df = pd.read_csv(sys.argv[1])
    results = {}
    sdidx = df["Stand density index"]
    for species in df["Species"].unique():
        ssp = str(species)
        results[ssp] = {}
        shit = df[["Species", "Stand density index"]]
        for density in sorted(list(sdidx.unique())):
            results[ssp][str(density)] = shit[(sdidx == density) & (shit["Species"] == species)].shape[0]
    with open("stand_density_counts.json", "w") as f:
        json.dump(results, f, indent=4, cls=encoder)


if __name__ == "__main__":
    main()

