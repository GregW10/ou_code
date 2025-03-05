#!/usr/bin/env python3

# STANDARD DEVIATION IS CALCULATED USING BESSEL'S CORRECTION!

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.tools.tools as smtt
import statsmodels.regression.linear_model as smrl


veg = "https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s350/tma02"


def main():
    if len(sys.argv) != 2:
        print("Usage: ./state.py <state>", file=sys.stderr)
        sys.exit(1)
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{siunitx}"
    df = pd.read_csv(f"{veg}/murica_leadCrime_data.csv")
    df = df.loc[df["state"].apply(lambda s: s.lower()) == sys.argv[1].lower()]
    lead = df["prop. children > 10 µg/dL"].mean()
    crime = df["violent crime rate (per 100000 people)"].mean()
    stdl = df["prop. children > 10 µg/dL"].std()
    stdc = df["violent crime rate (per 100000 people)"].std()
    seml = df["prop. children > 10 µg/dL"].sem()
    semc = df["violent crime rate (per 100000 people)"].sem()
    fyear = df["year"].min()
    lyear = df["year"].max()
    with open(f"{sys.argv[1]}_summary.csv", "w") as f:
        f.write("state,first year,last year,mean prop. Pb (> 10 µg/dL),mean crime (per 100000),STD prop. Pb (> 10 µg/dL),STD crime (per 100000),"
                "SEM prop. Pb (> 10 µg/dL),SEM crime (per 100000)\n")
        f.write(f"{sys.argv[1]},{fyear},{lyear},{lead},{crime},{stdl},{stdc},{seml},{semc}\n")
    print(f"Observation period: {fyear}-{lyear}")
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.scatter([], [], label="")
    ax1.scatter(df["year"], df["violent crime rate (per 100000 people)"], marker="x", color="red", label="Crime rate")
    ax2.scatter(df["year"], df["prop. children > 10 µg/dL"], marker="o", color="green",
                label="Children $[\\text{Pb}] > \\SI{10}{\\micro\gram\per\deci\liter}$")
    ax1.plot(df["year"], df["violent crime rate (per 100000 people)"], marker="x", color="orange")
    ax2.plot(df["year"], df["prop. children > 10 µg/dL"], marker="o", color="purple")
    ax1.set_title("Incidence of Crime and Proportion of Children with $>\\SI{10}{\\micro\gram\per\deci\liter}$ Lead\nin Blood in " + 
                 sys.argv[1] + f" Over {fyear}-{lyear}")
    ax1.set_xlabel("Year")
    ax2.set_ylabel("Mean Proportion of Children with $>\\SI{10}{\\micro\gram\per\deci\liter}$ in Blood")
    ax1.set_ylabel("Mean Incidence of Crime (per 100K people)")
    ax1.legend(loc="upper right", bbox_to_anchor=(0.99, 0.99))
    ax2.legend(loc="upper right", bbox_to_anchor=(0.99, 0.90))
    fig.savefig(f"{sys.argv[1]}_crime_rate_and_leadProp.pdf")


if __name__ == "__main__":
    main()

