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
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{siunitx}"
    dfwtot = pd.read_csv(f"{veg}/murica_leadCrime_data.csv")
    df = dfwtot.loc[dfwtot["state"] != "U.S. Totals"]
    states = df["state"].unique()
    # print(states)
    # print(states.shape[0])
    # print(df)
    lead = np.empty((states.shape[0]))
    crime = np.empty((states.shape[0]))
    stdl = np.empty((states.shape[0]))
    stdc = np.empty((states.shape[0]))
    seml = np.empty((states.shape[0]))
    semc = np.empty((states.shape[0]))
    fyears = np.empty((states.shape[0]), dtype=np.int32)
    lyears = np.empty((states.shape[0]), dtype=np.int32)
    with open("all_states_summary.csv", "w") as f:
        f.write("state,first year,last year,mean prop. Pb (> 10 µg/dL),mean crime (per 100000),STD prop. Pb (> 10 µg/dL),STD crime (per 100000),"
                "SEM prop. Pb (> 10 µg/dL),SEM crime (per 100000)\n")
        for i, state in enumerate(states):
            ds = df.loc[df["state"] == state]
            lead[i] = ds["prop. children > 10 µg/dL"].mean()
            crime[i] = ds["violent crime rate (per 100000 people)"].mean()
            stdl[i] = ds["prop. children > 10 µg/dL"].std()
            stdc[i] = ds["violent crime rate (per 100000 people)"].std()
            seml[i] = ds["prop. children > 10 µg/dL"].sem()
            semc[i] = ds["violent crime rate (per 100000 people)"].sem()
            fyears[i] = ds["year"].min()
            lyears[i] = ds["year"].max()
            f.write(f"{state},{fyears[i]},{lyears[i]},{lead[i]},{crime[i]},{stdl[i]},{stdc[i]},{seml[i]},{semc[i]}\n")
    # if maxcount > 1:
    print(f"Mean prop. lead conc. > 10 µg/dL in children: {np.mean(lead)}\nMean crime incidence: {np.mean(crime)} per 100K people")
    miny = np.min(fyears)
    maxy = np.max(lyears)
    print(f"Observation period: {miny}-{maxy}" + (" for all years" if all(fyears == miny) and all(lyears == maxy) else ""))
    res = smrl.OLS(crime, smtt.add_constant(lead)).fit()
    c, m = res.params
    stats = {"N": lead.shape[0], "intercept": c, "slope": m, "R^2": res.rsquared,
             "P_intercept": res.pvalues[0], "P_slope": res.pvalues[1], "F": res.fvalue}
    with open("all_states_summary_statistics.json", "w") as f:
        json.dump(stats, f, indent=4)
    fig, ax = plt.subplots()
    ax.scatter(lead, crime, marker="x", color="red")
    ax.errorbar(lead, crime, yerr=semc, capsize=2.5, fmt="none", label="SEM")
    ax.plot([np.min(lead), np.max(lead)], [m*np.min(lead) + c, m*np.max(lead) + c], color="green", label="Line of best fit")
    ax.set_title("Incidence of Violent Crime vs Proportion of Children with $>\\SI{10}{\\micro\gram\per\deci\liter}$\nLead in Blood in " + 
                  str(states.shape[0]) + f" U.S. States Over {miny}-{maxy}")
    ax.set_xlabel("Mean Proportion of Children with $>\\SI{10}{\\micro\gram\per\deci\liter}$ in Blood")
    ax.set_ylabel("Mean Incidence of Violent Crime (per 100K people)")
    ax.legend()
    fig.savefig("crime_rate_vs_leadProp.pdf")


if __name__ == "__main__":
    main()

