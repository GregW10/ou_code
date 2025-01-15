#!/usr/bin/python3

import math


def main():
    print("Question a")
    uval_nogap = 2.03 # W m^-2 K^-1
    uval_gap = 1.49 # W m^-2 K^-1
    perc_change = 100*(abs(uval_nogap - uval_gap)/uval_nogap)
    print(f"Percentage change: {perc_change}%")

    print("Question b\nNone - all in table 2.8 in SG2.")

    print("Question c")

    deg_days = 1_800 # degree days
    base_temp = 15.5 # degC

    # mean_temp_diff = deg_days/365.25

    uval = 0.4 # W m^-2 K^-1

    # print(f"Mean temperature difference: {mean_temp_diff} degC")

    ahl = uval*deg_days*86_400
    ahl_kWh = ahl/3_600_000

    print(f"Annual heat loss: {ahl} J/m^2 = {ahl_kWh} kWh")

    

if __name__ == "__main__":
    main()

