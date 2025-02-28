#!/usr/bin/python3

# BESSEL'S CORRECTION IS USED IN THIS DOCUMENT FOR STDDEV

import sys
import json
import time
import boto3
import requests
import argparse
import itertools
import numpy as np
import pandas as pd
import scipy.stats as spstat
import matplotlib.pyplot as plt
import statsmodels.tools as smtt
import statsmodels.regression.linear_model as smrl

rat_key = {"A":  "1w", "B":  "6w", "C":  "8w", "D":  "9w", "E": "10w",
           "F": "11c", "G": "14c", "H": "15c", "I": "16c", "J": "19c"}
rat_key_inv = {v: k for k, v in rat_key.items()}

veg = "https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s295/tma02"


def main():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{siunitx}"
    j = requests.get(f"{veg}/lipid_summary.json").json()
    print(j)
    fig, ax = plt.subplots()
    lab, data = ["Warm", "Cold"], [j["warm-bat"]["predicted-depot-lipid-mass"]["mean"]/1_000,
                                   j["cold-bat"]["predicted-depot-lipid-mass"]["mean"]/1_000]
    yerr = [j["warm-bat"]["predicted-depot-lipid-mass"]["std"]/1_000,
            j["cold-bat"]["predicted-depot-lipid-mass"]["std"]/1_000]    
    ax.bar(lab, data, color="navy")
    ax.errorbar(lab, data, yerr=yerr, fmt="none", color="red", capsize=5.0, label="Standard Deviation")
    ax.set_title("BAT Depot Lipid Mass in Warm- and Cold-Adapted Rats")
    ax.set_xlabel("Group")
    ax.set_ylabel("Lipid Mass in Depot ($\\si{\milli\gram}$)")
    ax.legend()
    ax.plot()
    fig.savefig("BAT_depot_size.pdf")

if __name__ == "__main__":
    main()

