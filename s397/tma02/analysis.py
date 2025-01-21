#!/usr/bin/python3

import sys
import math
import json
import argparse
import numpy as np
import pandas as pd
import scipy.stats as spstat
import matplotlib.pyplot as plt
import statsmodels.tools.tools as smtt
import statsmodels.regression.linear_model as smrl


def replace_chars(s: str):
    res = ""
    for c in s:
        if c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.":
            res += '_'
        else:
            res += c
    return res


def main():
    parser = argparse.ArgumentParser(prog="Phenology Analyser")
    parser.add_argument("fname")
    parser.add_argument("-s", "--show", action="store_true")
    parser.add_argument("--species", default="quercus robur")
    args = parser.parse_args()
    org = args.species
    args.species = args.species.lower()
    resname = f"results_{replace_chars(args.species)}_" + ".".join(args.fname.split('.')[0:-1]) + ".json"
    df = pd.read_csv(args.fname, dtype={"Species": str})
    # df["Species"] = df["Species"].astype(str)
    """if pd.isna(pd.to_numeric(["shit"], errors="coerce")):
        print("hoho")
        sys.exit(1)
    else:
        sys.exit(0)"""
    sdata = df.loc[[s.lower() == args.species for s in df["Species"]]]
    # print(sdata)
    # print(df["Species"].to_string())
    results = {}
    args.species = org # args.species[0].upper() + (args.species[1:] if len(args.species) > 1 else "")
    print(f"Part 1 - Test for significant variation between Canopy Cover Indices in {args.species} trees with "
          "different urbanisation categories.")
    # print(qrobur)
    urb_can = {}
    for urb_idx, cancov_idx in zip(sdata["Urbanisation index"], sdata["Canopy index"]):
        if cancov_idx != cancov_idx:
            continue
        if urb_idx in urb_can:
            urb_can[urb_idx].append(cancov_idx)
        else:
            urb_can[urb_idx] = [cancov_idx]
    # urb_can = dict(sorted(urb_can.items())) # not actually necessary
    """print(urb_can)
    print(*urb_can)
    print(*urb_can.values())"""
    f_val, p_val = spstat.f_oneway(*urb_can.values())
    print(f"F-statistic: {f_val}, P-value: {p_val}")
    results["urbanisation-canopy_cover"] = {"F": f_val, "P": p_val}
    #####################################################
    print(f"\n######\nPart 2 - Test for significant variation between Canopy Cover indices in {args.species} trees with"
          " different stand density categories.")
    sden_can = {}
    for sden_idx, cancov_idx in zip(sdata["Stand density index"], sdata["Canopy index"]):
        if cancov_idx != cancov_idx:
            continue
        if sden_idx in sden_can:
            sden_can[sden_idx].append(cancov_idx)
        else:
            sden_can[sden_idx] = [cancov_idx]
    f_val, p_val = spstat.f_oneway(*sden_can.values())
    print(f"F-statistic: {f_val}, P-value: {p_val}")
    results["stand_density-canopy_cover"] = {"F": f_val, "P": p_val}
    #####################################################
    print(f"\n#####\nPart 3 - Regression analysis between latitude and canopy cover index for {args.species}.")
    lat_cc = sdata[["Latitude", "Canopy index"]].dropna()
    lat = smtt.add_constant(lat_cc["Latitude"].to_numpy())
    cc = lat_cc["Canopy index"].to_numpy()
    del lat_cc
    regres = smrl.OLS(cc, lat).fit()
    results["latitude-canopy_cover"] = {"intercept": regres.params[0], "slope": regres.params[1],
                                        "F": regres.fvalue, "P": regres.pvalues[1], "R2": regres.rsquared}
    #####################################################
    """print("###########\nPart 4 - Regression analysis between latitude and canopy cover index for Q. petraea.")
    lat_cc = df.loc[[s.lower() == "quercus petraea" for s in df["Species"]]][["Latitude", "Canopy index"]].dropna()
    lat = smtt.add_constant(lat_cc["Latitude"].to_numpy())
    cc = lat_cc["Canopy index"].to_numpy()
    del lat_cc
    regres = smrl.OLS(cc, lat).fit()
    results["latitude-canopy_cover(q.petraea)"] = {"intercept": regres.params[0], "slope": regres.params[1],
                                                   "F": regres.fvalue, "P": regres.pvalues[1], "R2": regres.rsquared}
    #####################################################
    """
    results["note"] = f"Results are for {args.species}."
    with open(resname, "w") as r:
        json.dump(results, r, indent=4)
    #####################################################
    if args.show:
        pass



if __name__ == "__main__":
    main()
