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

standard_mass = 30 # mg
edson_vol = 6 # ml


def rad(area):
    return np.sqrt(area/np.pi)


def vol(area):
    return (4/3)*rad(area)*area


def lipid_ug_per_mg_tissue(conc, vol=edson_vol, mass=standard_mass):
    # expects [conc] = mg/ml, [vol] = ml, [mass] = mg
    return (conc*vol/mass)*1_000 # ug/mg


# def isnormal(arr, p=0.05):
#     return bool(spstat.shapiro(arr)[1] > p)


def main():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{siunitx}"
    parser = argparse.ArgumentParser(prog="analysis")
    parser.add_argument("-u", "--upload", action="store_true")
    parser.add_argument("-p", "--plot", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--shapiro-pvalue", "--shapiro-pval", "--spval", default=0.05, type=float)
    args = parser.parse_args()
    if args.quiet:
        pfunc = lambda x, *args: None
    else:
        pfunc = print
    j = requests.get(f"{veg}/info.json").json()
    pfunc(j)
    grid_area = float(j["microscope"]["grid-area"]["value"])*10**int(j["microscope"]["grid-area"]["exponent"])
    pixel_size = int(j["microscope"]["pixel-size"]["numerator"])/int(j["microscope"]["pixel-size"]["denominator"])
    pfunc(f"Pixel size: {pixel_size} m")
    fat_density = float(j["adipose-tissue-density"])
    pfunc(f"Grid area = {grid_area} m^2")
    # ################################################## CALCULATE MEAN CELL VALUES AND CELL DENSITY
    fat_rats = pd.read_csv(f"{veg}/fat_rats.csv")
    for c in ['w', 'b']:
        fat_rats[f"mean_num_{c}at"] = (fat_rats[f"{c}c1"] + fat_rats[f"{c}c2"] + fat_rats[f"{c}c3"])/3
        fat_rats[f"mean_cell_area_{c}at(m^2)"] = grid_area/fat_rats[f"mean_num_{c}at"]
        fat_rats[f"mean_cell_vol_{c}at(m^3)"] = vol(fat_rats[f"mean_cell_area_{c}at(m^2)"])
        fat_rats[f"mean_cell_mass_{c}at(kg)"] = fat_density*fat_rats[f"mean_cell_vol_{c}at(m^3)"]
        fat_rats[f"mean_cells_per_mg_{c}at(mg^-1)"] = 1/(1_000_000*fat_rats[f"mean_cell_mass_{c}at(kg)"])
    pfunc(fat_rats)
    fat_rats.to_csv("processed_fat_rats.csv", index=False)
    # ################################################# OBTAIN LIPID MODEL
    cal = pd.read_csv(f"{veg}/lipid_calibration.csv")
    cal["mean"] = cal.iloc[:, 1:].apply(lambda r: r.mean(), axis=1)
    cal.to_csv("processed_lipid_calibration.csv", index=False)
    pfunc(cal)
    res = smrl.OLS(cal["mean"], smtt.add_constant(cal["concentration(mg/ml)"])).fit()
    pfunc(res.params)
    intercept, slope = res.params.iloc[0], res.params.iloc[1]
    with open("lipid_calibration_curve.csv", "w") as f:
        f.write("intercept,slope,intercept_p-value,slope_p-value,R^2,F\n")
        f.write(f"{intercept},{slope},{res.pvalues.iloc[0]},{res.pvalues.iloc[1]},{res.rsquared},{res.fvalue}\n")
    pfunc(f"y = {slope}x + {intercept}")
    conc = cal["concentration(mg/ml)"].to_numpy()
    conc = np.hstack((conc.reshape((conc.shape[0], 1)), np.ones(shape=(conc.shape[0], 1))))
    means = cal["mean"].to_numpy().reshape((conc.shape[0], 1))
    pfunc(conc)
    pfunc(means)
    npres = np.linalg.lstsq(conc, means)
    pfunc(npres)
    if args.plot:
        fig, ax = plt.subplots()
        ax.plot(conc[:, 0], slope*conc[:, 0] + intercept, label="Line of best fit", color="purple")
        ax.scatter(conc[:, 0], means[:, 0], marker="x", color="red")
        ax.set_title("Spectrophotometer Calibration Curve for Lipid")
        ax.set_xlabel("Concentration ($\si{\milli\gram\per\milli\liter}$)")
        ax.set_ylabel("Absorbance (arbitrary units)")
        ax.legend()
        fig.savefig("lipid_calibration.png")
    # ##################################################### USE LIPID MODEL
    pfunc(cal)
    abs_names = list(itertools.product(["Warm", "Cold"], ["w", "b"]))
    absorbances = [pd.read_csv(f"{veg}/{temp.lower()}_lipid_{c}at.csv") for temp, c in abs_names]
    lipid = {}
    masses = [fat_rats.iloc[:5]["WAT_mass(g)"], fat_rats.iloc[:5]["BAT_mass(g)"],
              fat_rats.iloc[5:]["WAT_mass(g)"], fat_rats.iloc[5:]["BAT_mass(g)"]]
    cell_lipid_mass = {}
    mnnn = None
    nmmm = None
    for df, mass, (temp, c) in zip(absorbances, masses, abs_names):
        pfunc(mass)
        mass = mass.reset_index(drop=True)
        df["mean"] = df.iloc[:, 1:].apply(lambda r: r.mean(), axis=1)
        df["predicted_concentration(mg/ml)"] = (df["mean"] - intercept)/slope
        df["predicted_lipid_per_mg(ug/mg)"] = lipid_ug_per_mg_tissue(df["predicted_concentration(mg/ml)"])
        df["predicted_depot_lipid_mass(ug)"] = df["predicted_lipid_per_mg(ug/mg)"]*mass*1_000
        lipid[f"{temp.lower()}-{c}at"] = {"predicted-lipid-concentration": {
                                              "mean": df["predicted_concentration(mg/ml)"].mean(),
                                              "std": df["predicted_concentration(mg/ml)"].std(),
                                              "SEM": df["predicted_concentration(mg/ml)"].sem(),
                                              "units": "mg/ml",
                                              "shapiro-p-value": spstat.shapiro(df["predicted_concentration(mg/ml)"])[1]
                                          },
                                          "predicted-lipid-content": {
                                              "mean": df["predicted_lipid_per_mg(ug/mg)"].mean(),
                                              "std": df["predicted_lipid_per_mg(ug/mg)"].std(),
                                              "SEM": df["predicted_lipid_per_mg(ug/mg)"].sem(),
                                              "units": "ug/mg",
                                              "shapiro-p-value": spstat.shapiro(df["predicted_lipid_per_mg(ug/mg)"])[1]
                                          },
                                          "predicted-depot-lipid-mass": {
                                              "mean": df["predicted_depot_lipid_mass(ug)"].mean(),
                                              "std": df["predicted_depot_lipid_mass(ug)"].std(),
                                              "SEM": df["predicted_depot_lipid_mass(ug)"].sem(),
                                              "units": "ug",
                                              "shapiro-p-value": spstat.shapiro(df["predicted_depot_lipid_mass(ug)"])[1]
                                          },
                                          "N": df.shape[0]
                                         }
        pfunc(df)
        df.to_csv(f"processed_{temp.lower()}_lipid_{c}at.csv", index=False)
        if temp.lower() == "warm":
            if mnnn is None:
                mnnn = fat_rats[f"mean_cell_mass_{c}at(kg)"].iloc[:5].mean()
            sfac = mnnn*1_000_000
            cell_lipid_mass[f"warm-{c}at"] = \
                    {"mean": lipid[f"warm-{c}at"]["predicted-lipid-content"]["mean"]*sfac,
                     "std": lipid[f"warm-{c}at"]["predicted-lipid-content"]["std"]*sfac}
        else:
            if nmmm is None:
                nmmm = fat_rats[f"mean_cell_mass_{c}at(kg)"].iloc[5:].mean()
            sfac = nmmm*1_000_000
            cell_lipid_mass[f"cold-{c}at"] = \
                    {"mean": lipid[f"cold-{c}at"]["predicted-lipid-content"]["mean"]*sfac,
                     "std": lipid[f"cold-{c}at"]["predicted-lipid-content"]["std"]*sfac}
    with open("lipid_summary.json", "w") as f:
        json.dump(lipid, f, indent=4)
    cell_lipid_mass["units"] = "ug"
    with open("mean_lipid_mass_per_cell.json", "w") as f:
        json.dump(cell_lipid_mass, f, indent=4)
    # ########################################## STATISTICAL ANALYSIS OF LIPIDS
    lipstats = {}
    bs = []
    for df1, df2, n1, n2 in ((absorbances[0], absorbances[2], abs_names[0], abs_names[2]),
                             (absorbances[1], absorbances[3], abs_names[1], abs_names[3])):
        pfunc(f"One = {n1}\nTwo = {n2}")
        lipstats[f"{n1[0].lower()}{n1[1].upper()}AT-{n2[0].lower()}{n2[1].upper()}AT"] = {}
        for idx, (v1, v2) in enumerate(zip(list(lipid[f"{n1[0].lower()}-{n1[1]}at"].items())[:-1],
                                           list(lipid[f"{n2[0].lower()}-{n2[1]}at"].items())[:-1]), start=7):
            pfunc(v1, v2)
            pfunc(type(v1))
            pfunc(type(v1[1]))
            if v1[1]["shapiro-p-value"] > args.shapiro_pvalue and v2[1]["shapiro-p-value"] > args.shapiro_pvalue:
                pfunc("PERFORMING T-TEST")
                res = spstat.ttest_ind(df1.iloc[:, idx], df2.iloc[:, idx])
                lipstats[f"{n1[0].lower()}{n1[1].upper()}AT-{n2[0].lower()}{n2[1].upper()}AT"][v1[0]] = \
                    {"test-type": "t-test", "statistic": res.statistic, "p-value": res.pvalue}
                bs.append(True)
            else:
                pfunc("PERFORMING MANN-WHITNEY U-TEST")
                res = spstat.mannwhitneyu(df1.iloc[:, idx], df2.iloc[:, idx])
                lipstats[f"{n1[0].lower()}{n1[1].upper()}AT-{n2[0].lower()}{n2[1].upper()}AT"][v1[0]] = \
                    {"test-type": "U-test", "statistic": res.statistic, "p-value": res.pvalue}
                bs.append(False)
        #for nq in ["predicted-lipid-concentration", "predicted-lipid-content", "predicted-depot-lipid-mass"]:
        #    if lipid[f"{n1[0].lower()}-{n1[1]}at"][nq]["is-normal(p>0.05)"] and lipid[f"{n2[0].lower()}-{n2[1]}at"][nq]["is-normal(p>0.05)"]:
    if all(bs):
        fstatname = "lipid_statistics_t-test.json"
    elif any(bs):
        fstatname = "lipid_statistics.json"
    else:
        fstatname = "lipid_statistics_U-test.json"
    pfunc("----------------\n-------------------------\n---------------")
    pfunc(bs)
    pfunc(fstatname)
    with open(fstatname, "w") as f:
        json.dump(lipstats, f, indent=4)
    # ########################################## MEAN PATH
    coords_wat = fat_rats.iloc[:, [5, 6, 8, 9, 11, 12]]
    coords_bat = fat_rats.iloc[:, [14, 15, 17, 18, 20, 21]]
    coords_wat = coords_wat.rename(lambda cname: cname.strip("w"), axis=1)
    coords_bat = coords_bat.rename(lambda cname: cname.strip("b"), axis=1)
    # pfunc(coords_wat)
    # pfunc(coords_bat)
    coords = pd.concat([coords_wat, coords_bat])
    pfunc(coords)
    x_12 = (coords["c2_x"] - coords["c1_x"]).to_numpy()
    x_23 = (coords["c3_x"] - coords["c2_x"]).to_numpy()
    y_12 = (coords["c2_y"] - coords["c1_y"]).to_numpy()
    y_23 = (coords["c3_y"] - coords["c2_y"]).to_numpy()
    x_13 = (coords["c3_x"] - coords["c1_x"]).to_numpy()
    y_13 = (coords["c3_y"] - coords["c1_y"]).to_numpy()
    x_12p = (coords["c2_x"] - coords["c1_x"]).to_numpy()*pixel_size
    x_23p = (coords["c3_x"] - coords["c2_x"]).to_numpy()*pixel_size
    y_12p = (coords["c2_y"] - coords["c1_y"]).to_numpy()*pixel_size
    y_23p = (coords["c3_y"] - coords["c2_y"]).to_numpy()*pixel_size
    x_13p = (coords["c3_x"] - coords["c1_x"]).to_numpy()*pixel_size
    y_13p = (coords["c3_y"] - coords["c1_y"]).to_numpy()*pixel_size
    nnn = x_12.shape[0]
    assert(all(nnn == sp.shape[0] for sp in [x_23, y_12, y_23, x_13, y_13]))
    x_1, y_1 = np.mean(x_12), np.mean(y_12)
    x_2, y_2 = np.mean(x_23), np.mean(y_23)
    x_t, y_t = x_1 + x_2, y_1 + y_2
    x_1p, y_1p = np.mean(x_12p), np.mean(y_12p)
    x_2p, y_2p = np.mean(x_23p), np.mean(y_23p)
    x_tp, y_tp = x_1p + x_2p, y_1p + y_2p
    pfunc(x_1, y_1)
    pfunc(x_2, y_2)
    pfunc(x_t, y_t)
    x_t, y_t = np.mean(x_13), np.mean(y_13)
    pfunc(x_t, y_t)
    pfunc(x_1p, y_1p)
    pfunc(x_2p, y_2p)
    pfunc(x_tp, y_tp)
    x_tp, y_tp = np.mean(x_13p), np.mean(y_13p)
    pfunc(x_tp, y_tp)
    path = {"N": nnn}
    path["pixel-displacement"] = {"x1-x2": {"mean": x_1, "std": np.std(x_12, ddof=1)},
                                  "x2-x3": {"mean": x_2, "std": np.std(x_23, ddof=1)},
                                  "x1-x3": {"mean": x_t, "std": np.std(x_13, ddof=1)},
                                  "y1-y2": {"mean": y_1, "std": np.std(y_12, ddof=1)},
                                  "y2-y3": {"mean": y_2, "std": np.std(y_23, ddof=1)},
                                  "y1-y3": {"mean": y_t, "std": np.std(y_13, ddof=1)}}
    path["physical-displacement"] = {"x1-x2": {"mean": x_1p, "std": np.std(x_12p, ddof=1)},
                                     "x2-x3": {"mean": x_2p, "std": np.std(x_23p, ddof=1)},
                                     "x1-x3": {"mean": x_tp, "std": np.std(x_13p, ddof=1)},
                                     "y1-y2": {"mean": y_1p, "std": np.std(y_12p, ddof=1)},
                                     "y2-y3": {"mean": y_2p, "std": np.std(y_23p, ddof=1)},
                                     "y1-y3": {"mean": y_tp, "std": np.std(y_13p, ddof=1)}}
    path["pixel-displacement-units"] = "unitless (number of pixels)"
    path["physical-displacemente-units"] = "metres"
    with open("mean_path.json", "w") as f:
        json.dump(path, f, indent=4)
    # #################################### PROTEIN CURVE
    """buffpath = f"{veg}/buff_rats.csv"
    buffpath_c = f"{'.'.join(buffpath.split('.')[:-1])}_corrected.csv"
    pfunc(buffpath)
    pfunc(buffpath_c)
    for path in [buffpath, buffpath_c]:
        buff = pd.read_csv(path)
        pfunc(buff)"""
    ll_path = f"ll_protein_calibration.csv"
    aa_path = f"aa_protein_calibration.csv"
    for path in [ll_path, aa_path]:
        df = pd.read_csv(f"{veg}/" + path)
        s = df.shape
        pfunc(s)
        df["mean"] = df.iloc[:,     1:].apply(lambda r: r.mean(), axis=1)
        df["std"]  = df.iloc[:, 1:s[1]].apply(lambda r: r.std(),  axis=1)
        df["SEM"]  = df.iloc[:, 1:s[1]].apply(lambda r: r.sem(),  axis=1)
        pfunc(df)
        df.to_csv("processed_" + path, index=False)
        res = smrl.OLS(df["mean"], smtt.add_constant(df["conc.(ug/ml)"])).fit()
        intercept = res.params.iloc[0]
        slope = res.params.iloc[1]
        pfunc(res.params)
        pfunc(res.pvalues)
        pfunc(type(res.pvalues))
        pfunc(f"y = {slope}x + {intercept}")
        splitted = path.split('.')[0]
        with open(splitted + "_curve.csv", "w") as f:
            f.write("intercept,slope,intercept_p-value,slope_p-value,R^2,F\n")
            f.write(f"{intercept},{slope},{res.pvalues.iloc[0]},{res.pvalues.iloc[1]},{res.rsquared},{res.fvalue}\n")
        if args.plot:
            fig, ax = plt.subplots()
            ax.plot(df["conc.(ug/ml)"], slope*df["conc.(ug/ml)"] + intercept, label="Line of best fit", color="green")
            ax.scatter(df["conc.(ug/ml)"], df["mean"], marker="x", color="red")
            ax.set_title(f"{splitted[:2].upper()} Labs Spectrophotometer Calibration Curve for Protein")
            ax.set_xlabel("Concentration ($\si{\milli\gram\per\milli\liter}$)")
            ax.set_ylabel("Absorbance (arbitrary units)")
            ax.legend()
            fig.savefig(splitted + ".png")
    # ############################################## FILE UPLOAD
    if args.upload:
        pfunc("Uploading files...")


if __name__ == "__main__":
    main()

