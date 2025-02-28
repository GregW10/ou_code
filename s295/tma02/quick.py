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
    counts = {}
    for temp in ["warm", "cold"]:
        fat_rats = pd.read_csv(f"{veg}/fat_rats_{temp}.csv")
        print(fat_rats)
        for c in ['w', 'b']:
            fat_rats[f"mean_num_{c}at"] = (fat_rats[f"{c}c1"] + fat_rats[f"{c}c2"] + fat_rats[f"{c}c3"])/3.0
            counts[f"{temp}-{c.upper()}AT"] = {"mean": fat_rats[f"mean_num_{c}at"].mean(),
                                                "std": fat_rats[f"mean_num_{c}at"].std(),
                                                "SEM": fat_rats[f"mean_num_{c}at"].sem()}
    with open("counts.json", "w") as f:
        json.dump(counts, f, indent=4)

if __name__ == "__main__":
    main()

