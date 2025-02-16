#!/usr/bin/python3

import sys
import json
import numpy as np
import pandas as pd
from analysis import encoder
import matplotlib.pyplot as plt
from scipy.stats import f_oneway


def main():
    if len(sys.argv) > 4:
        sys.exit(1)
    recp = None
    if len(sys.argv) == 4:
        recp = sys.argv[3]
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
    jname_prefix = "".join(sys.argv[1].split('.')[0:-1])
    with open(jname_prefix + "_standDensityCounts.json", "w") as f:
        json.dump(results, f, indent=4, cls=encoder)
    df = df[df["Species"] == sys.argv[2]]
    df_diam = df[["Tree diameter (cm)", "Stand density index"]]
    densities = {}
    for density in sorted(list(df["Stand density index"].unique())):
        densities[density] = df_diam[df_diam["Stand density index"] == density]["Tree diameter (cm)"].to_numpy()
    F, P = f_oneway(*densities.values())
    with open(jname_prefix + "_standDensityANOVA.json", "w") as f:
        json.dump({"F": F, "P": P}, f, indent=4)
    fig, ax = plt.subplots()
    y = np.array([np.mean(arr) for arr in densities.values()])
    ax.bar(densities.keys(), y)
    ax.errorbar(densities.keys(), y, fmt="none", yerr=[np.std(arr) for arr in densities.values()], color="red", capsize=5.0)
    ax.set_xticks([*densities.keys()])
    ax.set_xlabel("Stand Density Index")
    ax.set_ylabel("Mean Tree Diameter (cm)")
    ax.set_title("Mean \\textit{" + sys.argv[2] + "} Tree Diameter by Stand Density" + (f"\nin Recording Period {recp}" if recp else ""))
    # plt.show()
    fig.savefig("treeDiameterVsStandDensity" + (f"_recPeriod{recp}" if recp else "") + ".pdf")


if __name__ == "__main__":
    main()

