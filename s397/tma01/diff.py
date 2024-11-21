#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse


def main():
    parser = argparse.ArgumentParser(prog="Diff")
    parser.add_argument("--file1", default="file1.csv")
    parser.add_argument("--file2", default="file2.csv")
    parser.add_argument("--col1", default="Sapflow (l day-1)")
    parser.add_argument("--col2", default="Sapflow (l day-1)")
    args = parser.parse_args()
    df1 = pd.read_csv(args.file1)
    df2 = pd.read_csv(args.file2)
    


if __name__ == "__main__":
    main()
