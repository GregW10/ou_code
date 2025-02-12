#!/usr/bin/python3

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{gensymb}\\usepackage{siunitx}"
    df1 = pd.read_csv(sys.argv[1])
    df2 = pd.read_csv(sys.argv[2])
    long1 = df1["Longitude"]
    long2 = df2["Longitude"]
    long = np.concatenate((long1, long2))
    fig, ax = plt.subplots()
    bins = np.arange(start=-100, stop=180, step=10)
    ax.hist(long, bins=bins, log=True, edgecolor="black", linewidth=1)
    ax.set_title("Longitude Distribution")
    ax.set_xlabel("Longitude ($^{\circ}$)")
    ax.set_ylabel("Count")
    ax.set_xticks(np.arange(-100, 180, 20))
    fig.savefig("longitude_plot.pdf")


if __name__ == "__main__":
    main()

