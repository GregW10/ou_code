#!/usr/bin/python3

import sup

def main():
    co2_lhv_gCO2_per_MJ = 57
    co2_lhv = co2_lhv_gCO2_per_MJ/(1_000*1_000_000) # (kgCO2/J) convert to SI units
    ccgt_eff = 0.54
    ccgt_emission = co2_lhv*(1/ccgt_eff) # (kgCO2/J)
    print(ccgt_emission)
    ccgt_emission_kgCO2_per_kWh = ccgt_emission*sup.kWh
    print(f"{ccgt_emission_kgCO2_per_kWh} kgCO2/kWh")


if __name__ == "__main__":
    main()

