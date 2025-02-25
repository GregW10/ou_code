#!/usr/bin/python3

import sys
import json
import requests
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.tools as smtt
import statsmodels.regression.linear_model as smrl

rat_key = {"A": "1w", "B": "6w", "C": "8w", "D": "9w", "E": "10w",
           "F": "11c", "G": "14c", "H": "15c", "I": "16c", "J": "19c"}
rat_key_inv = {v: k for k, v in rat_key.items()}

veg = "https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s295/tma02"


def rad(area):
    return (area/np.pi)**(1/2)


def vol(area):
    return (4/3)*rad(area)*area


def lipid_ug_per_mg_tissue(conc, vol=6, mass=30):
    # expects [conc] = mg/ml, [vol] = ml, [mass] = mg
    return conc*vol/mass


def main():
    j = requests.get(f"{veg}/info.json").json()
    print(j)
    grid_area = float(j["microscope"]["grid-area"]["value"])*10**int(j["microscope"]["grid-area"]["exponent"])
    fat_density = float(j["adipose-tissue-density"])
    print(grid_area)
    fat_rats = pd.read_csv(f"{veg}/fat_rats.csv")
    for c in ['w', 'b']:
        fat_rats[f"mean_num_{c}at"] = (fat_rats[f"{c}c1"] + fat_rats[f"{c}c2"] + fat_rats[f"{c}c3"])/3
        fat_rats[f"mean_cell_area_{c}at"] = grid_area/fat_rats[f"mean_num_{c}at"]
        fat_rats[f"mean_cell_vol_{c}at"] = vol(fat_rats[f"mean_cell_area_{c}at"])
        fat_rats[f"mean_cell_mass_{c}at"] = fat_density*fat_rats[f"mean_cell_vol_{c}at"]
        fat_rats[f"mean_cells_per_mg_{c}at"] = 1/(1_000_000*fat_rats[f"mean_cell_mass_{c}at"])
    print(fat_rats)
    fat_rats.to_csv("processed_fat_rats.csv")
    # #################################################
    cal = pd.read_csv(f"{veg}/lipid_calibration.csv")
    cal["mean"] = cal.iloc[:, 1:].apply(lambda r: r.mean(), axis=1)
    cal.to_csv("processed_lipid_calibration.csv")
    print(cal)
    res = smrl.OLS(cal["mean"], smtt.add_constant(cal["concentration(mg/ml)"])).fit()
    print(res.params)
    c, m = res.params
    print(f"y = {m}x + {c}")
    conc = cal["concentration(mg/ml)"].to_numpy()
    conc = np.hstack((conc.reshape((conc.shape[0], 1)), np.ones(shape=(conc.shape[0], 1))))
    means = cal["mean"].to_numpy().reshape((conc.shape[0], 1))
    print(conc)
    print(means)
    npres = np.linalg.lstsq(conc, means)
    print(npres)
    fig, ax = plt.subplots()
    ax.plot(conc[:, 0], m*conc[:, 0] + c)
    ax.scatter(conc[:, 0], means[:, 0], marker="x", color="red")
    fig.savefig("calibration.png")
    

if __name__ == "__main__":
    main()

