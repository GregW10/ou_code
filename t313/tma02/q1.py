#!/usr/bin/env python3

import math
import sup
import sys
import os

diny = 365.25

blue = ""
bold = ""
reset = ""


def main():
    if os.isatty(sys.stdout.fileno()):
        blue = "\033[38;5;12m"
        bold = "\033[1m"
        reset = "\033[0m"
    print(f"{blue}######################################\n{bold}Question a{reset}")
    annual_prod = 2009 # kWh/year
    daily_prod = annual_prod/diny
    print(f"Daily production = {daily_prod} kWh/day")
    # ###############################################
    print(f"\n{blue}#########################################\nQuestion b{reset}")
    num_years = 10
    panels_installation = 1999 # pounds
    frame_equipment = 800
    OandM = 50 # pounds per year
    totOandM = OandM*num_years
    bank_interest = 0.05 # per year
    annuity = sup.annuity(panels_installation, bank_interest, num_years)
    tot_pay = annuity*num_years
    tot_spent = tot_pay + frame_equipment + totOandM # total money spent on the panels and their usage over "num_years" years
    print(f"Annuity = {annuity} pounds per year\nTotal amount to pay back to bank over {num_years}-year period = {tot_pay} pounds\nTotal money spent = {tot_spent} pounds")
    self_consumption = 0.7
    import_price = 0.245
    export_price = 0.095 # pounds per kWh
    energy_used  = self_consumption*annual_prod*num_years # kWh used in "num_years" years
    energy_sold  = (1 - self_consumption)*annual_prod*num_years # kWh sold in "num_years" years
    money_saved  = energy_used*import_price
    money_earned = energy_sold*export_price # pounds earned over "num_years" years
    saved_earned = money_saved + money_earned
    print(f"Total money saved from not importing electricity over {num_years} years = {money_saved} pounds")
    print(f"Total money earned from selling electricity at a self-consumption rate of {self_consumption} over {num_years} years = {money_earned} pounds")
    print(f"Savings + earnings = {saved_earned} pounds over {num_years} years")
    print(f"Net gain over {num_years} years = {saved_earned - tot_spent}")
    # ####################################################################
    print(f"\n{blue}#########################################\nQuestion d{reset}")
    manfEcost = 250 # kWh/m^2
    num_panels = 12
    panel_area = 0.88 # m^2/panel
    total_area = num_panels*panel_area
    print(f"Total panel area is {total_area} m^2")
    energy_cost = manfEcost*total_area
    time_to_recover = energy_cost/annual_prod
    print(f"The energy cost of creating these panels is {energy_cost} kWh\nThus, the time to recover this energy through use is {time_to_recover} year{'s' if time_to_recover != 1 else ''}")





if __name__ == "__main__":
    main()

