#!/usr/bin/python3

import sys
import math


ocon = 4_000 # annual heat consumption for hot water (kWh/year)
bolef = 0.75

lhoil_lhv_mjkg = 42.6 # MJ/kg
lhoil_lhv_kwhl = 9.9 # kWh/L
lhoil_co2em = 2.7 # kgCO2/L


def main():
    print("Question a")
    q_oil = ocon/bolef
    print(f"Heating energy supplied by oil: {q_oil} kWh/year")

    print("\nQuestion b")
    oil_litres = q_oil/lhoil_lhv_kwhl
    oil_co2em = oil_litres*lhoil_co2em
    print(f"Litres of oil used: {oil_litres} L/year\nThis equals: {oil_co2em} kgCO2/year")

    print("\nQuestion c")
    pv_area = 5.5 # m^2
    sol_heat_eff = 0.33
    insol = 890 # kWh m^-2 yr^-1

    pv_final_heat = insol*pv_area*sol_heat_eff
    pv_heat_prop_wh = pv_final_heat/ocon
    print(f"Heat available from PV for water heating: {pv_final_heat} kWh/year\n"
          f"This represents {pv_heat_prop_wh*100}% of the heat required to heat water.")


if __name__ == "__main__":
    main()
