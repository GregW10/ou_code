#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp
import argparse
import requests
import hashlib
import json
import sys
import os
import io

bucket = "https://veggiebucket.ams3.digitaloceanspaces.com"
folder = f"{bucket}/ou_stuff/s295/tma03"
endpoint = f"{folder}/data.csv"
sha512 = f"{endpoint}.sha512"

# def_obs_time = 20 # minutes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--observation-time", default=20)
    parser.add_argument("-s", "--summary", default="summary.json")
    args = parser.parse_args()
    r = requests.get(endpoint)
    if r.status_code != 200:
        print(f"Error: could not fetch \"{endpoint}\"", file=sys.stderr)
        sys.exit(1)
    data = r.content
    r = requests.get(sha512)
    if r.status_code != 200:
        print(f"Error: could not fetch \"{endpoint}\"", file=sys.stderr)
        sys.exit(1)
    sha = r.content.decode()
    if hashlib.sha512(data).hexdigest() != sha.split()[0]:
        print("Error: computed checksums of CSV data do not match.", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(io.StringIO(data.decode()))
    print(df)
    rp1_s, rp1_p = sp.stats.shapiro(df["recPeriod1-pollinations"])
    rp2_s, rp2_p = sp.stats.shapiro(df["recPeriod2-pollinations"])
    normal = True
    if rp1_p >= 0.05:
        print("Insufficient evidence to prove that the recording-period 1 pollination distribution is not normal.")
        normal = False
    if rp2_p >= 0.05:
        print("Insufficient evidence to prove that the recording-period 2 pollination distribution is not normal.")
        normal = not normal
    with open("normality-test.json", "w") as f:
        json.dump({"N": df.shape[0],
                   "recPeriod1": {"test-statistic": rp1_s,"p-value": rp1_p},
                   "recPeriod2": {"test-statistic": rp2_s,"p-value": rp2_p},
                   "normality-assumed": normal}, f, indent=4)
    if normal:
        print("Normality of data assumed.\nPerforming t-test.")
        test = sp.stats.ttest_ind
        fname = "t-test.json"
    else:
        print("Data cannot be assumed to be normal.\nPerforming Mann-Whitney U test.")
        test = sp.stats.mannwhitneyu
        fname = "mann-whitney-u.json"
    res = test(df["recPeriod1-pollinations"],
               df["recPeriod2-pollinations"])
    # print(res)
    with open(fname, "w") as f:
        json.dump({"N": df.shape[0],
                   "statistic": res.statistic,
                   "p-value": res.pvalue,
                   "df": res.df}, f, indent=4)
    # print(plt.rcParams)
    means = [df["recPeriod1-pollinations"].mean(), df["recPeriod2-pollinations"].mean()]
    stds  = [df["recPeriod1-pollinations"].std(),  df["recPeriod2-pollinations"].std()]
    sems  = [df["recPeriod1-pollinations"].sem(),  df["recPeriod2-pollinations"].sem()]
    with open(args.summary, "w") as f:
        json.dump({
                "rec-period-1": {
                        "N":    df.shape[0],
                        "mean": means[0],
                        "std":  stds[0],
                        "sem":  sems[0]
                    },
                "rec-period-2": {
                        "N":    df.shape[0],
                        "mean": means[1],
                        "std":  stds[1],
                        "sem":  sems[1]
                    }
            }, f, indent=4)
    plt.rcParams["text.usetex"] = True
    plt.rcParams["text.latex.preamble"] = r"\usepackage{siunitx}\usepackage{amsmath}"
    plt.rcParams["font.family"] = "serif"
    fig, ax = plt.subplots()
    ax.bar(["Morning", "Afternoon"], means)
    ax.errorbar(["Morning", "Afternoon"], means,
                yerr=sems,
                fmt="none", capsize=10, color="red", label="SEM")
    ax.set_title("Mean Number of Pollination Events per $\\SI{" + str(args.observation_time) + "}{\\minute}$\nin Morning vs Afternoon")
    ax.set_xlabel("Time Period")
    ax.set_ylabel("Mean Number of Pollination Events per $\\SI{" + str(args.observation_time) + "}{\\minute}$")
    ax.legend()
    fig.savefig("pollinations.pdf")



if __name__ == "__main__":
    main()

# nonce=6803647219
