#!/usr/bin/python3

import sys
import json
import numpy as np
import pandas as pd
from analysis import encoder
import matplotlib.pyplot as plt
from scipy.stats import f_oneway


def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{gensymb}\\usepackage{siunitx}"
    df = pd.read_csv(sys.argv[1])
    results = {}
    sdidx = df["Stand density index"]
    sdidx_unique = sorted(list(sdidx.unique()))
    df_specsdi = df[["Species", "Stand density index"]]
    for species in df["Species"].unique():
        ssp = str(species)
        results[ssp] = {}
        for density in sdidx_unique:
            results[ssp][str(density)] = df_specsdi[(sdidx == density) & (df_specsdi["Species"] == species)].shape[0]
    jname = "".join(sys.argv[1].split('.')[0:-1]) + ".json"
    with open(jname, "w") as f:
        json.dump(results, f, indent=4, cls=encoder)
    df = df[df["Species"] == sys.argv[2]]
    df_diam = df[["Tree diameter (cm)", "Stand density index"]]
    densities = {}
    for density in sdidx_unique:
        densities[density] = df_diam[df_diam["Stand density index"] == density]["Tree diameter (cm)"].to_numpy()
    F, P = f_oneway(*densities.values())
    with open("stand_density_results.json", "w") as f:
        json.dump({"F": F, "P": P}, f, indent=4)
    fig, ax = plt.subplots()
    ax.bar(densities.keys(), [np.mean(arr) for arr in densities.values()])
    plt.show()


if __name__ == "__main__":
    main()

