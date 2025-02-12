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
    alt1 = df1["Altitude"]
    alt2 = df2["Altitude"]
    alt = np.concatenate((alt1, alt2))
    fig, ax = plt.subplots()
    bins = np.arange(start=0, stop=2400, step=50)
    ax.hist(alt, bins=bins, log=True, edgecolor="black", linewidth=1)
    ax.set_title("Altitude Distribution")
    ax.set_xlabel("Altitude ($\\si{\\meter}$)")
    ax.set_ylabel("Count")
    ax.set_xticks(np.arange(0, 2400, 200))
    fig.savefig("altitude_plot.pdf")


if __name__ == "__main__":
    main()

