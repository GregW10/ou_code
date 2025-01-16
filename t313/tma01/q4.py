#!/usr/bin/python3

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

days_in_months = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


def main():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["text.latex.preamble"] = "\\usepackage{siunitx}"
    if len(sys.argv) != 3:
        print("Error: no data-files specified.", file=sys.stderr)
        sys.exit(1)
    print("Question 2.i")
    # outputs = np.zeros(shape=(12,))
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
        month_names = lines[0].split(',')
        outputs = np.array([float(s) for s in lines[-1].split(',')]) # mean daily outputs per month in Wh/day
    # yearly_output = 0.0 # Wh/year
    # for ndays, output in zip(days_in_months, outputs):
        # yearly_output += ndays*output
    yearly_output = np.sum(days_in_months*outputs)
    print(f"YEARLY OUTPUT: {yearly_output} Wh/year")
    monthly_output = (yearly_output/12)/1_000 # kWh/month
    print(f"MONTHLY OUTPUT: {monthly_output} kWh/year")
    """mean = np.mean(outputs) # mean number of watt-hours per day over the entire year
    print(f"Mean number of watt-hours per day over entire year: {mean} Wh")
    num_days_per_month = (3*365 + 366)/(4*12)
    print(f"Num. days per month: {num_days_per_month}")
    monthly_output = (mean*num_days_per_month)/1_000 # kWh
    print(f"The mean monthly output is: {monthly_output} kWh/month")"""

    print("Question 2.ii")
    with open(sys.argv[2], "r") as f:
        loads = np.array([float(s) for s in f.readlines()[-1].split(',')])
    mean = np.sum(days_in_months*loads)/365.25
    print(f"Mean daily power load: {mean} Wh/day")
    # mean = np.mean(outputs)
    minn = np.min(loads)
    maxx = np.max(loads)
    minpd = ((mean - minn)/mean)*100
    maxpd = ((maxx - mean)/mean)*100
    yearly_output = np.sum(loads*days_in_months)
    print(f"Mean: {mean}, min: {minn}, max: {maxx}, min. p.d.: {minpd}, max. p.d.: {maxpd}\nYO: {yearly_output},")

    print("Question 2.iii")
    # month_names = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    fig, ax = plt.subplots()
    ax.plot(month_names, outputs/1_000, marker='x', markerfacecolor="red", markeredgecolor="red", label="Output")
    ax.plot(month_names, loads/1_000, marker='x', markerfacecolor="green", markeredgecolor="green", label="Load")
    # ax.set_xlim(0)
    ax.set_ylim(0)
    ax.set_title("Daily Outputs and Loads by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Power ($\\si{\\kilo\\si{\\watt\\hour}\\per\\day}$)")
    ax.legend()
    # plt.show()
    fig.savefig("outputs_and_loads.pdf")



if __name__ == "__main__":
    main()
