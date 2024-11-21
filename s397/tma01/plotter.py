#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import argparse
import glob
import os


def main():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["text.latex.preamble"] = "\\usepackage{amsmath}\n\\usepackage{siunitx}"
    parser = argparse.ArgumentParser(prog="Plotter")
    parser.add_argument("--data-dir", default="./")
    parser.add_argument("-o", "--output-dir", default=None)
    parser.add_argument("--path-filter", default="")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--otitle", default="Title")
    parser.add_argument("--oxlabel", default="$x$-axis")
    parser.add_argument("--oylabel", default="$y$-axis")
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    if args.output_dir is None:
        args.output_dir = args.data_dir
    if not args.data_dir.endswith("/"):
        args.data_dir += "/"
    if not args.output_dir.endswith("/"):
        args.output_dir += "/"
    os.makedirs(args.output_dir, exist_ok=True)
    file_paths = sorted(glob.glob(f"{args.data_dir}*{args.path_filter}*.csv"))[::-1]
    if len(file_paths) == 0:
        raise RuntimeError("Error: no CSV files found in data directory.")
    dframes = {fpath: pd.read_csv(fpath) for fpath in file_paths}
    ofig, oax = plt.subplots()
    oax.set_title(args.otitle)
    oax.set_xlabel(args.oxlabel)
    oax.set_ylabel(args.oylabel)
    for fpath, dframe in zip(dframes.keys(), dframes.values()):
        qname = dframe.columns[0].replace("%", r"\%")
        sname = dframe.columns[1].replace("l day-1", r"$\si{\liter\per\day}$").replace("apflow", "ap-Flow")
        qvals = dframe.iloc[:, 0].to_numpy()
        svals = dframe.iloc[:, 1].to_numpy()
        splitted = qname.split()
        bname = splitted[0] if not "umidity" in qname else f"{splitted[0]} {splitted[1]}"
        fig, ax = plt.subplots()
        ax.plot(qvals, svals)
        fname = fpath.split('/')[-1]
        oax.plot(qvals, svals, label=fname.split('_')[0])
        ax.set_title(f"Plot of Predicted Sap-Flow vs {bname} for\n{bname}-based Model")
        ax.set_xlabel(f"{qname}")
        ax.set_ylabel(f"{sname}")
        print(fpath)
        if args.show:
            print("showin")
            plt.show()
        fig.savefig(f"{args.output_dir}{fname.split('.')[0]}.png", dpi=args.dpi)
        # plt.clf()
        plt.close(fig)
    oax.legend()
    ofig.savefig(f"{args.output_dir}overall_figure.png", dpi=args.dpi)


if __name__ == "__main__":
    main()
