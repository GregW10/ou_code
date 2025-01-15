#!/usr/bin/python3

import sys
import json
import pandas as pd
import matplotlib.pyplot as plt


def main():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{siunitx}"
    if len(sys.argv) != 2:
        print("Error: no data-file specified.", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(sys.argv[1])
    data = {}
    for cname, c in df.items():
        data[cname] = c.to_numpy()
        print(f"C = {c.to_numpy()}")
    # with open("data.json", "w") as f:
    #     json.dump(data, f)
    fig, ax = plt.subplots()
    for key, val in data.items():
        if key.lower() == "year" or key.lower() == "total renewables":
            continue
        ax.plot(data["Year"], val, label=key)
    ax.set_xlim(min(data["Year"]))
    ax.set_ylim(0)
    ax.set_title("UK Production of Electrical Energy from Low-Carbon Sources")
    ax.set_xlabel("Year")
    ax.set_ylabel("Electricity Generated ($\\si{\\tera\\si{\\watt\\hour}}$)")
    ax.legend()
    # plt.show()
    fig.savefig("electricity_data_q3.pdf")
    # print(plt.rcParams)


if __name__ == "__main__":
    main()
