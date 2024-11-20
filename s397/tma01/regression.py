#!/usr/bin/python3

import statsmodels.tools.tools as smtt
import statsmodels.regression.linear_model as smrl
import pandas as pd
import numpy as np
import sys
import os
import argparse
import glob
import json
import calendar


def main():
    parser = argparse.ArgumentParser(prog="Regression")
    parser.add_argument("--data-dir", default="./")
    parser.add_argument("-o", "--out-path", default="data.json")
    parser.add_argument("--start-year", default=2019, type=int)
    parser.add_argument("--end-year", default=2024, type=int)
    # parser.add_argument("-s", "--apply-models", default=False)
    parser.add_argument("--sim-data", default=None)
    parser.add_argument("-s", "--sim-out-dir", default=None)
    args = parser.parse_args()
    if args.start_year > args.end_year:
        raise ValueError("Error: starting year must be less than or equal to ending year.")
    print(f"Data directory: {args.data_dir}")
    if not args.data_dir.endswith("/"):
        args.data_dir += '/'
    monthly_data_files = []
    y = args.start_year
    while y <= args.end_year:
        monthly_data_files.append(glob.glob(f"{args.data_dir}*{y}*.csv")[0])
        y += 1
    monthly_dataframes = [pd.read_csv(f) for f in monthly_data_files]
    models = {}
    summary = {}
    y = args.start_year
    for df in monthly_dataframes:
        if df["Sapflow (l day-1)"].empty:
            y += 1
            continue
        df["Date"] = pd.to_datetime(df["Date"])
        # print(df["Date"].dt.month == 7)
        # print(df[df["Date"].dt.month == 7])
        models[y] = {}
        summary[y] = {"temperature": {}, "humidity": {}, "radiation": {}, "sapflow": {}}
        sliced = df[["Date", "Mean Temperature (degC)", "Sapflow (l day-1)"]].dropna()
        # print(sliced)
        if sliced.shape[0] != 0:
            month = 1
            while month <= 12:
                mdf = sliced[sliced["Date"].dt.month == month]
                if mdf.empty:
                    month += 1
                    continue
                temp = smtt.add_constant(mdf["Mean Temperature (degC)"].to_numpy())
                tempsap = mdf["Sapflow (l day-1)"].to_numpy()
                models[y].update({calendar.month_name[month]: {"Temperature-Sapflow": [smrl.OLS(tempsap, temp).fit(), mdf.shape[0]]}})
                summary[y]["temperature"].update({calendar.month_name[month]: {"mean": np.mean(temp[:, 1]), "std": np.std(temp[:, 1]), "min": np.min(temp[:, 1]), "max": np.max(temp[:, 1])}})
                month += 1
        sliced = df[["Date", "Mean Relative Humidity (%)", "Sapflow (l day-1)"]].dropna()
        if sliced.shape[0] != 0:
            month = 1
            while month <= 12:
                mdf = sliced[sliced["Date"].dt.month == month]
                if mdf.empty:
                    month += 1
                    continue
                hum = smtt.add_constant(mdf["Mean Relative Humidity (%)"].to_numpy())
                humsap = mdf["Sapflow (l day-1)"].to_numpy()
                if calendar.month_name[month] in models[y]:
                    models[y][calendar.month_name[month]].update({"Humidity-Sapflow": [smrl.OLS(humsap, hum).fit(), mdf.shape[0]]})
                else:
                    models[y].update({calendar.month_name[month]: {"Humidity-Sapflow": [smrl.OLS(humsap, hum).fit(), mdf.shape[0]]}})
                summary[y]["humidity"].update({calendar.month_name[month]: {"mean": np.mean(hum[:, 1]), "std": np.std(hum[:, 1]), "min": np.min(hum[:, 1]), "max": np.max(hum[:, 1])}})
                month += 1
        sliced = df[["Date", "Mean Radiation (Wm-2)", "Sapflow (l day-1)"]].dropna()
        if sliced.shape[0] != 0:
            month = 1
            while month <= 12:
                mdf = sliced[sliced["Date"].dt.month == month]
                if mdf.empty:
                    month += 1
                    continue
                rad = smtt.add_constant(mdf["Mean Radiation (Wm-2)"].to_numpy())
                radsap = mdf["Sapflow (l day-1)"].to_numpy()
                if calendar.month_name[month] in models[y]:
                    models[y][calendar.month_name[month]].update({"Radiation-Sapflow": [smrl.OLS(radsap, rad).fit(), mdf.shape[0]]})
                else:
                    models[y].update({calendar.month_name[month]: {"Radiation-Sapflow": [smrl.OLS(radsap, rad).fit(), mdf.shape[0]]}})
                summary[y]["radiation"].update({calendar.month_name[month]: {"mean": np.mean(rad[:, 1]), "std": np.std(rad[:, 1]), "min": np.min(rad[:, 1]), "max": np.max(rad[:, 1])}})
                month += 1
        month = 1
        while month <= 12:
            mdf = df[df["Date"].dt.month == month]["Sapflow (l day-1)"].dropna()
            if mdf.empty:
                month += 1
                continue
            # print(mdf)
            summary[y]["sapflow"].update({calendar.month_name[month]: {"mean": mdf.mean(), "std": mdf.std(ddof=0), "min": mdf.min(), "max": mdf.max(), "total": mdf.sum()}})
            month += 1
        y += 1
    # print(summary)
    summary["units"] = {"temperature": "degC", "humidity": "%", "radiation": "W m^-2", "sapflow": "L day^-1", "total-sapflow": "L"}
    with open("summary.json", "w") as fsum:
        json.dump(summary, fsum, indent=4)
    fitted = {}
    for year, model_months_dict in zip(models.keys(), models.values()):
        fitted[year] = {}
        for month, model_dict in zip(model_months_dict.keys(), model_months_dict.values()):
            fitted[year][month] = {}
            for model_name, model in zip(model_dict.keys(), model_dict.values()):
                fitted[year][month].update({model_name: {"intercept": model[0].params[0], "slope": model[0].params[1],
                                                         "P": model[0].pvalues[1], "F": model[0].fvalue, "R2": model[0].rsquared, "N": model[1]}})
    with open(args.out_path, "w") as f:
        json.dump(fitted, f, indent=4)
    if not args.sim_out_dir:
        sys.exit(0)
    simul_data_file = args.sim_data if args.sim_data else glob.glob(f"{args.data_dir}*simul*.csv")[0]
    simdat = pd.read_csv(simul_data_file)
    if simdat.shape[0] == 0:
        raise RuntimeError("Error: simulated data file empty.")
    simdat.dropna(inplace=True)
    simtemp = simdat["Temperature (degC)"].to_numpy()
    simhum = simdat["Relative Humidity (%)"].to_numpy()
    simrad = simdat["Radiation (Wm-2)"].to_numpy()
    os.makedirs(args.sim_out_dir, exist_ok=True)
    if not args.sim_out_dir.endswith("/"):
        args.sim_out_dir += "/"
    NaNs = np.empty(simtemp.shape)
    NaNs[:] = np.nan
    for year, months_dict in zip(fitted.keys(), fitted.values()):
        for month, models_dict in zip(months_dict.keys(), months_dict.values()):
            tempsap_pred = (simtemp*models_dict["Temperature-Sapflow"]["slope"] + models_dict["Temperature-Sapflow"]["intercept"]) if "Temperature-Sapflow" in models_dict else NaNs
            humsap_pred = (simhum*models_dict["Humidity-Sapflow"]["slope"] + models_dict["Humidity-Sapflow"]["intercept"]) if "Humidity-Sapflow" in models_dict else NaNs
            radsap_pred = (simrad*models_dict["Radiation-Sapflow"]["slope"] + models_dict["Radiation-Sapflow"]["intercept"]) if "Radiation-Sapflow" in models_dict else NaNs
            with open(f"{args.sim_out_dir}{month}{year}.csv", "w") as f:
                f.write("Temperature-Pred. Sapflow (l day-1),Humidity-Pred. Sapflow (l day-1),Radiation-Pred. Sapflow (l day-1)\n")
                for t, h, r in zip(tempsap_pred, humsap_pred, radsap_pred):
                    f.write(f"{'' if t != t else t},{'' if h != h else h},{'' if r != r else r}\n")
    
    

if __name__ == "__main__":
    main()
