#!/usr/bin/env python3

# STANDARD DEVIATION IS CALCULATED USING BESSEL'S CORRECTION!

import sys
import json
import string
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.tools.tools as smtt
import statsmodels.regression.linear_model as smrl


veg = "https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s350/tma02"


def repp(s: str):
    accepted = string.ascii_letters + string.digits + "_."
    for c in s:
        if c not in accepted:
            s = s.replace(c, '_')
    return s


def main():
    if len(sys.argv) < 2:
        print("Usage: ./state.py <state1> [<state2>] [<state3>] [...]", file=sys.stderr)
        sys.exit(1)
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{siunitx}"
    dfo = pd.read_csv(f"{veg}/murica_leadCrime_data.csv")
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    strstate = ""
    for state in sys.argv[1:]:
        df = dfo.loc[dfo["state"].apply(lambda s: s.lower()) == state.lower()]
        lead = df["prop. children > 10 µg/dL"].mean()
        crime = df["violent crime rate (per 100000 people)"].mean()
        stdl = df["prop. children > 10 µg/dL"].std()
        stdc = df["violent crime rate (per 100000 people)"].std()
        seml = df["prop. children > 10 µg/dL"].sem()
        semc = df["violent crime rate (per 100000 people)"].sem()
        fyear = df["year"].min()
        lyear = df["year"].max()
        repped = repp(state)
        with open(f"{repped}_summary.csv", "w") as f:
            f.write("state,first year,last year,mean prop. Pb (> 10 µg/dL),mean crime (per 100000),STD prop. Pb (> 10 µg/dL),STD crime (per 100000),"
                    "SEM prop. Pb (> 10 µg/dL),SEM crime (per 100000)\n")
            f.write(f"{state},{fyear},{lyear},{lead},{crime},{stdl},{stdc},{seml},{semc}\n")
        print(f"{state} observation period: {fyear}-{lyear}")
        ax1.plot(df["year"], df["violent crime rate (per 100000 people)"], marker="x", label=f"{state} crime rate")
        ax2.plot(df["year"], df["prop. children > 10 µg/dL"], marker="o",
                    label=(state + " child prop. $[\\text{Pb}] > \\SI{10}{\\micro\gram\per\deci\liter}$"))
        strstate += repped + '_'
    ax1.set_title("Incidence of Violent Crime and Proportion of Children with $>\\SI{10}{\\micro\gram\per\deci\liter}$\nLead in Blood " + 
                 f"Over {fyear}-{lyear}")
    ax1.set_xlabel("Year")
    ax2.set_ylabel("Mean Proportion of Children with $>\\SI{10}{\\micro\gram\per\deci\liter}$ in Blood")
    ax1.set_ylabel("Mean Incidence of Violent Crime (per 100K people)")
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    print(handles1)
    print(labels1)
    print(handles2)
    print(labels2)
    ax1.legend(handles1 + handles2, labels1 + labels2)#loc="upper right", bbox_to_anchor=(0.99, 0.99))
    # ax2.legend()#loc="upper right", bbox_to_anchor=(0.99, 0.90))
    fig.savefig(f"{strstate}crime_rate_and_leadProp.pdf")


if __name__ == "__main__":
    main()

