#!/usr/bin/python3

import sys
import math
import json
import hashlib
import requests
import argparse
import numpy as np
import pandas as pd
import scipy.stats as spstat
import matplotlib.pyplot as plt
import statsmodels.tools.tools as smtt
import statsmodels.regression.linear_model as smrl

inst = isinstance


class encoder(json.JSONEncoder):
    def default(self, ob):
        if inst(ob, np.int64):
            return int(ob)
        return super().default(ob)


def replace_chars(s: str):
    if len(s) == 0:
        return ""
    # if s[0] == '-':
    #     s[0] = '_'
    res = ""
    for c in s:
        if c.upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-":
            res += '_'
        else:
            res += c
    return res


def download(which: int):
    endpoint = f"https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s397/tma02/phenology_recPeriod{which}.csv"
    endpoint_sha512 = endpoint + ".sha512"
    content = requests.get(endpoint).content
    hr = requests.get(endpoint_sha512).text.split()[0]
    hc = hashlib.sha512(content).hexdigest()
    if hr != hc:
        print("Error: sha-512 hash of the downloaded file \"{endpoint}\" does not match true sha-512 hash.")
    with open(f"phenology_recPeriod{which}.csv", "wb") as f:
        f.write(content)


def write_summary(df: pd.DataFrame, recp: int):
    results = {}
    species = df["Species"]#.dropna()
    unique = list(species.unique())
    dunique = {}
    for spec in unique:
        dunique[spec] = species[species == spec].shape[0]
    results["species counts"] = {spec: num for spec, num in sorted(dunique.items(), key=lambda it: it[1], reverse=True)}
    for label in ["Latitude", "Longitude", "Altitude", "Tree diameter (cm)", "Urbanisation index", "Stand density index", "Canopy index", "Phenological index"]:
        quantity = df[label].dropna().to_numpy()
        results[label.lower()] = {"N": quantity.shape[0], "mean": np.mean(quantity), "std": np.std(quantity),
                                  "min": np.min(quantity), "max": np.max(quantity)}
    with open(f"overall_summary_recPeriod{recp}.json", "w") as f:
        json.dump(results, f, indent=4, cls=encoder)


def main():
    parser = argparse.ArgumentParser(prog="Phenology Analyser")
    parser.add_argument("fname")
    parser.add_argument("-p", "--plot", action="store_true")
    parser.add_argument("--species", default="quercus robur")
    parser.add_argument("-r", "--recp", default=1, type=int)
    parser.add_argument("-s", "--std", action="store_true")
    args = parser.parse_args()
    if args.fname == "/1":
        download(1)
        args.fname = "phenology_recPeriod1.csv"
        args.recp = 1
    elif args.fname == "/2":
        download(2)
        args.fname = "phenology_recPeriod2.csv"
        args.recp = 2
    org = args.species
    args.species = args.species.lower()
    resname = f"results_{replace_chars(args.species)}_" + ".".join(args.fname.split('.')[0:-1]) + ".json"
    df = pd.read_csv(args.fname)#, dtype={"Species": str})
    df["Species"] = df["Species"].astype(str)
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
    for key in urb_can:
        urb_can[key] = np.array(urb_can[key])
    urb_can = dict(sorted(urb_can.items())) # not actually necessary
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
    for key in sden_can:
        sden_can[key] = np.array(sden_can[key])
    sden_can = dict(sorted(sden_can.items())) # not actually necessary
    f_val, p_val = spstat.f_oneway(*sden_can.values())
    print(f"F-statistic: {f_val}, P-value: {p_val}")
    results["stand_density-canopy_cover"] = {"F": f_val, "P": p_val}
    #####################################################
    print(f"\n#####\nPart 3 - Regression analysis between latitude and canopy cover index for {args.species}.")
    lat_cc = sdata[["Latitude", "Canopy index"]].dropna()
    lat_arr = lat_cc["Latitude"].to_numpy()
    lat = smtt.add_constant(lat_arr)
    cc = lat_cc["Canopy index"].to_numpy()
    del lat_cc
    regres = smrl.OLS(cc, lat).fit()
    results["latitude-canopy_cover"] = {"intercept": regres.params[0], "slope": regres.params[1],
                                        "F": regres.fvalue, "P": regres.pvalues[1], "R2": regres.rsquared}
    print(f"y = {regres.params[1]}x + {regres.params[0]}")
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
    write_summary(df, args.recp)
    if not args.plot:
        sys.exit(0)
    ##################################################### PLOTTING BELOW
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{gensymb}"
    urb_cci_means = {}
    urb_cci_stds = {}
    for urb_idx, cci_arr in urb_can.items():
        # print(urb_idx)
        # print(cci_arr)
        urb_cci_means[urb_idx] = np.mean(cci_arr)
        if args.std:
            urb_cci_stds[urb_idx] = np.std(cci_arr)
        print(f"Mean: {np.mean(cci_arr)}, std: {np.std(cci_arr)}, min: {np.min(cci_arr)}, max: {np.max(cci_arr)}")
    # print(urb_cci_means)
    fig, ax = plt.subplots()
    ax.bar(urb_cci_means.keys(), urb_cci_means.values())
    ax.set_xticks(list(urb_cci_means.keys()))
    if args.std:
        ax.errorbar(urb_cci_means.keys(), urb_cci_means.values(),
                    yerr=urb_cci_stds.values(), fmt="none", color="red", capsize=5.0)
    ax.set_xlabel("Urbanisation Index")
    ax.set_ylabel("Mean Canopy Cover Index")
    ax.set_title("Mean Canopy Cover Index vs Urbanisation Index in \\textit{" + args.species + "}\n"
                 f"During Recording Period {args.recp}")
    fig.savefig(f"urbCCI_plot_{replace_chars(args.species)}_" + ".".join(args.fname.split('.')[0:-1]) + ".pdf")
    # plt.show()
    # ########
    sden_cci_means = {}
    sden_cci_stds = {}
    for sden_idx, cci_arr in sden_can.items():
        # print(urb_idx)
        # print(cci_arr)
        sden_cci_means[sden_idx] = np.mean(cci_arr)
        if args.std:
            sden_cci_stds[sden_idx] = np.std(cci_arr)
        print(f"Mean: {np.mean(cci_arr)}, std: {np.std(cci_arr)}, min: {np.min(cci_arr)}, max: {np.max(cci_arr)}")
    # print(urb_cci_means)
    fig, ax = plt.subplots()
    ax.bar(sden_cci_means.keys(), sden_cci_means.values())
    ax.set_xticks(list(sden_cci_means.keys()))
    if args.std:
        ax.errorbar(sden_cci_means.keys(), sden_cci_means.values(),
                    yerr=sden_cci_stds.values(), fmt="none", color="red", capsize=5.0)
    ax.set_xlabel("Stand Density Index")
    ax.set_ylabel("Mean Canopy Cover Index")
    ax.set_title("Mean Canopy Cover Index vs Stand Density Index in \\textit{" + args.species + "}\n"
                 f"During Recording Period {args.recp}")
    fig.savefig(f"standDensityCCI_plot_{replace_chars(args.species)}_" + ".".join(args.fname.split('.')[0:-1]) + ".pdf")
    # plt.show()
    # ########
    fig, ax = plt.subplots()
    ax.scatter(lat_arr, cc)
    lmin = np.min(lat_arr)
    lmax = np.max(lat_arr)
    print(f"min. lat: {lmin}, max. lat: {lmax}")
    ax.plot([lmin, lmax],
            [regres.params[1]*lmin + regres.params[0],
             regres.params[1]*lmax + regres.params[0]],
            color="red", label="Line of best fit")
    ax.set_xlabel("Latitude ($\\degree$)")
    ax.set_ylabel("Canopy Cover Index")
    ax.set_title("Canopy Cover Index vs Latitude in \\textit{" + args.species + "}\n"
                 f"During Recording Period {args.recp}")
    ax.legend()
    fig.savefig(f"latCCI_plot_{replace_chars(args.species)}_" + ".".join(args.fname.split('.')[0:-1]) + ".pdf")
    # plt.show()
    ##########################################################################




if __name__ == "__main__":
    main()
