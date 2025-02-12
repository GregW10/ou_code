#!/usr/bin/python3

import sys
import json


def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    with open(sys.argv[1], "r") as f:
        j1 = json.load(f)    
    with open(sys.argv[2], "r") as f:
        j2 = json.load(f)
    results = {}
    for (k1, v1), (k2, v2) in zip(j1.items(), j2.items()):
        if k1 != k2:
            print("Error: expected both JSONs to contain identical keys in the same order.", file=sys.stderr)
            sys.exit(1)
        if "N" not in v1:
            continue
        N = v1["N"] + v2["N"]
        results[k1] = {"N": N, "mean": (v1["N"]*v1["mean"] + v2["N"]*v2["mean"])/N,
                       "min": min(v1["min"], v2["min"]), "max": max(v1["max"], v2["max"])}
    with open("means.json", "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()

