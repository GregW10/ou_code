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
    lat1 = df1["Latitude"]
    lat2 = df2["Latitude"]
    lat = np.concatenate((lat1, lat2))
    fig, ax = plt.subplots()
    ax.hist(lat, bins=[-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70], log=True, edgecolor="black", linewidth=1)
    ax.set_title("Latitude Distribution")
    ax.set_xlabel("Latitude ($^{\circ}$)")
    ax.set_ylabel("Count")
    ax.set_xticks([-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70])
    fig.savefig("latitude_plot.pdf")


if __name__ == "__main__":
    main()

