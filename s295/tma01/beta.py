#!/usr/bin/python3

import matplotlib.pyplot as plt
import urllib.request
import pandas as pd
import numpy as np
import scipy.stats
import argparse
import hashlib
import glob
import json


def betas(Y: np.ndarray, y: np.ndarray, R: np.ndarray, r: np.ndarray):
    # Returns a tuple of beta_y values and beta_r values
    assert Y.shape == y.shape and y.shape == R.shape and R.shape == r.shape, "Error: input arrays must have the same shape."
    # print(Y)
    # print(y)
    # print(R)
    # print(r)
    Y[y == 0] += 1
    y[y == 0]  = 1
    R[r == 0] += 1
    r[r == 0]  = 1
    # print(Y)
    # print(y)
    # print(R)
    # print(r)
    # print("-------------------------------")
    log_Yoy = np.log10(Y/y)
    # log_Ror = np.log10(R/r)
    added = log_Yoy + np.log10(R/r) # log_Ror
    # return log_Yoy/added, log_Ror/added
    betay = log_Yoy/added
    return betay, 1 - betay


def main():
    plt.rcParams["text.usetex"] = True
    parser = argparse.ArgumentParser(prog="beta")
    parser.add_argument("-y", "--yellow-common-path", default=None)
    parser.add_argument("-r", "--red-common-path", default=None)
    parser.add_argument("--yellow-out", default="yellow_common_betas.csv")
    parser.add_argument("--red-out", default="red_common_betas.csv")
    parser.add_argument("--summary", default="summary.json")
    parser.add_argument("-s", "--show", action="store_true")
    parser.add_argument("-f", "--fig-path", default="medians.pdf")
    parser.add_argument("-u", "--u-test-path", default="U-test_summary.json")
    parser.add_argument("-d", "--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        resp = urllib.request.urlopen("https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s295/tma01/yellow_common.csv")
        yc_data = resp.read()
        resp.close()
        resp = urllib.request.urlopen("https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s295/tma01/red_common.csv")
        rc_data = resp.read()
        resp.close()
        resp = urllib.request.urlopen("https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s295/tma01/yellow_common.csv.sha512")
        yc_hash_data = resp.read()
        resp.close()
        resp = urllib.request.urlopen("https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/s295/tma01/red_common.csv.sha512")
        rc_hash_data = resp.read()
        resp.close()
        if yc_hash_data.decode().split()[0] != hashlib.sha512(yc_data).hexdigest():
            raise RuntimeError("Error: SHA-512 hash of downloaded \"yellow_common.csv\" does not match original hash.")
        if rc_hash_data.decode().split()[0] != hashlib.sha512(rc_data).hexdigest():
            raise RuntimeError("Error: SHA-512 hash of downloaded \"red_common.csv\" does not match original hash.")
        with open("yellow_common.csv", "wb") as f:
            f.write(yc_data)
        with open("red_common.csv", "wb") as f:
            f.write(rc_data)
        args.yellow_common_path = "yellow_common.csv"
        args.red_common_path = "red_common.csv"
    if not args.yellow_common_path:
        args.yellow_common_path = glob.glob("*yellow*.csv")[-1]
    if not args.red_common_path:
        args.red_common_path = glob.glob("*red*.csv")[-1]
    ydf = pd.read_csv(args.yellow_common_path)
    starty = ydf["total_start"].to_numpy()
    remy = ydf["total_remaining"].to_numpy()
    Yy = ydf["Y"].to_numpy()
    yy = ydf["y"].to_numpy()
    Ry = ydf["R"].to_numpy()
    ry = ydf["r"].to_numpy()
    if not np.all((Yy + Ry) == starty):
        raise ValueError(f"Error: \"Y\" and \"R\" columns in {args.yellow_common_path} do not sum to produce \"total_start\" column.")
    if not np.all((yy + ry) == remy):
        raise ValueError(f"Error: \"y\" and \"r\" columns in {args.yellow_common_path} do not sum to produce \"total_remaining\" column.")
    # print(starty, remy, Yy, yy, Ry, ry)
    rdf = pd.read_csv(args.red_common_path)
    startr = rdf["total_start"].to_numpy()
    remr = rdf["total_remaining"].to_numpy()
    Yr = rdf["Y"].to_numpy()
    yr = rdf["y"].to_numpy()
    Rr = rdf["R"].to_numpy()
    rr = rdf["r"].to_numpy()
    if not np.all((Yr + Rr) == startr):
        raise ValueError(f"Error: \"Y\" and \"R\" columns in {args.red_common_path} do not sum to produce \"total_start\" column.")
    if not np.all((yr + rr) == remr):
        raise ValueError(f"Error: \"y\" and \"r\" columns in {args.red_common_path} do not sum to produce \"total_remaining\" column.")
    # print(startr, remr, Yr, yr, Rr, rr)
    # print(ydf)
    # print(rdf)
    beta_yy, beta_ry = betas(Yy, yy, Ry, ry)
    beta_yr, beta_rr = betas(Yr, yr, Rr, rr)
    ycf = open(args.yellow_out, "w")
    rcf = open(args.red_out, "w")
    ycf.write("trial,beta_y,beta_r\n")
    rcf.write("trial,beta_y,beta_r\n")
    for i, (byy, bry, byr, brr) in enumerate(zip(beta_yy, beta_ry, beta_yr, beta_rr), start=1):
        ycf.write(f"{i},{byy},{bry}\n")
        rcf.write(f"{i},{byr},{brr}\n")
    ycf.close()
    rcf.close()
    summary = {}
    for name, arr in [("beta_yy", beta_yy), ("beta_ry", beta_ry), ("beta_yr", beta_yr), ("beta_rr", beta_rr)]:
        summary[name] = {"mean": np.mean(arr), "median": np.median(arr), "std": np.std(arr), "min": np.min(arr), "max": np.max(arr)}
    with open(args.summary, "w") as suf:
        json.dump(summary, suf, indent=4)
    labels = ["Yellow Common $\\beta_y$", "Yellow Common $\\beta_r$", "Red Common $\\beta_y$", "Red Common $\\beta_r$"]
    medians = [summary["beta_yy"]["median"], summary["beta_ry"]["median"], summary["beta_yr"]["median"], summary["beta_rr"]["median"]]
    fig, ax = plt.subplots()
    ax.bar(labels, medians, zorder=1)
    ax.set_ylim(0, 1)
    ax.set_title("Median $\\beta$ Values for the Four Sets of Selection Probabilities")
    ax.set_xlabel("Type of Selection Probability")
    ax.set_ylabel("Median $\\beta$ Value")
    ax.grid(axis="y", which="both", zorder=0)
    if args.show:
        plt.show()
    fig.savefig(args.fig_path)
    u_summ = {}
    u1_yyyr, pval_yyyr = scipy.stats.mannwhitneyu(beta_yy, beta_yr)
    u1_rrry, pval_rrry = scipy.stats.mannwhitneyu(beta_rr, beta_ry)
    u1_yrry, pval_yrry = scipy.stats.mannwhitneyu(beta_yr, beta_ry)
    u1_yyrr, pval_yyrr = scipy.stats.mannwhitneyu(beta_yy, beta_rr)
    u_summ["YYYR"] = {"U1": u1_yyyr, "U2": beta_yy.shape[0]*beta_yr.shape[0] - u1_yyyr, "p": pval_yyyr}
    u_summ["RRRY"] = {"U1": u1_rrry, "U2": beta_rr.shape[0]*beta_ry.shape[0] - u1_rrry, "p": pval_rrry}
    u_summ["YRRY"] = {"U1": u1_yrry, "U2": beta_yr.shape[0]*beta_ry.shape[0] - u1_yrry, "p": pval_yrry}
    u_summ["YYRR"] = {"U1": u1_yyrr, "U2": beta_yy.shape[0]*beta_rr.shape[0] - u1_yyrr, "p": pval_yyrr}
    u_summ["key"] = {"YYYR": "yellow-common-yellow-rare", "RRRY": "red-common-red-rare", "YRRY": "yellow-rare-red-rare", "YYRR": "yellow-common-red-common"}
    with open(args.u_test_path, "w") as f:
        json.dump(u_summ, f, indent=4)
    
    
    

if __name__ == "__main__":
    main()
