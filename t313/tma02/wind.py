#!/usr/bin/env python3

import sys
import json
import math
import argparse
import numpy as np
import pandas as pd


endpoint = "https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/t313/tma02/wind-speed-distributions.csv"
# sha = "https://veggiebucket.ams3.digitaloceanspaces.com/ou_stuff/t313/tma02/wind-speed-distributions.csv.sha512"


def log_speeds_err():
    pfunc("Error: invalid speeds format. Expected \"lo-hi\".", file=sys.stderr)
    sys.exit(1)


class encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.int64):
            return int(o)
        if isinstance(o, np.float64):
            return float(o)
        return super().default(o)


def main():
    parser = argparse.ArgumentParser(prog="wind-speed-calculator")
    parser.add_argument("-f", "--file", default=endpoint)
    parser.add_argument("-s", "--speeds", default="-")
    parser.add_argument("-o", "--outfile", default=None)
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()
    if '-' not in args.speeds:
        log_speeds_err()
    split = args.speeds.split('-')
    l = len(split)
    if l > 2:
        log_speeds_err()
    lo = 0.0
    hi = None
    if split[0]:
        lo = float(split[0])
    if split[1]:
        hi = float(split[1])
    df = pd.read_csv(args.file)
    max_windspeed = df["wind-speed"].max()
    if not hi:
        hi = float(max_windspeed)
    if math.floor(lo) == lo:
        lo = int(lo)
    if math.floor(hi) == hi:
        hi = int(hi)
    pfunc = print
    if args.quiet:
        pfunc = lambda *arguments: None
    pfunc(f"lo = {lo}, hi = {hi}")
    a_tothrs = df["site-A-hours"].sum()
    b_tothrs = df["site-B-hours"].sum()
    '''if math.floor(a_tothrs) == a_tothrs:
        a_tothrs = int(a_tothrs)
    else:
        a_tothrs = float(a_tothrs)
    if math.floor(b_tothrs) == b_tothrs:
        b_tothrs = int(b_tothrs)
    else:
        b_tothrs = float(b_tothrs)'''
    pfunc(f"A total hours = {a_tothrs}\nB total hours = {b_tothrs}")
    df = df[((df["wind-speed"] > lo) & (df["wind-speed"] <= hi))]
    winds = df["wind-speed"].to_numpy() - 0.5
    a_rnghrs = df["site-A-hours"].sum()
    b_rnghrs = df["site-B-hours"].sum()
    a_mws = (np.sum(winds*df["site-A-hours"].to_numpy())/a_rnghrs) if a_rnghrs > 0 else 0
    b_mws = (np.sum(winds*df["site-B-hours"].to_numpy())/b_rnghrs) if b_rnghrs > 0 else 0
    pfunc(f"Site A mean wind speed: {a_mws}\nSite B mean wind speed: {b_mws}")
    '''if math.floor(a_rnghrs) == a_rnghrs:
        a_rnghrs = int(a_rnghrs)
    else:
        a_rnghrs = float(a_rnghrs)
    if math.floor(b_rnghrs) == b_rnghrs:
        b_rnghrs = int(b_rnghrs)
    else:
        b_rnghrs = float(b_rnghrs)'''
    a_prop = a_rnghrs/a_tothrs
    b_prop = b_rnghrs/b_tothrs
    pfunc(f"Number of hours site A has wind speeds in ({lo}, {hi}] m/s = {a_rnghrs}\n"
          f"Number of hours site B has wind speeds in ({lo}, {hi}] m/s = {b_rnghrs}")
    pfunc(f"Proportion of time site A has wind speeds in ({lo}, {hi}] m/s = {a_prop}\n"
          f"Proportion of time site B has wind speeds in ({lo}, {hi}] m/s = {b_prop}")
    if not args.outfile:
        args.outfile = f"wind-speed-{lo}-{hi}-summary.json"
    with open(args.outfile, "w") as f:
        json.dump({"wind-speed": {"units": "m/s", "range": {"low": lo, "high": hi}},
                   "site-A": {"total-hours": a_tothrs, "within-range": {"hours": a_rnghrs, "proportion": a_prop, "mean-wind-speed": a_mws}},
                   "site-B": {"total-hours": b_tothrs, "within-range": {"hours": b_rnghrs, "proportion": b_prop, "mean-wind-speed": b_mws}}}, f, indent=4, cls=encoder)


if __name__ == "__main__":
    main()
