#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import sys


def ntp1(nt: float, K: float, lam: float):
    # assert(all([isinstance(val, float) for val in [nt, K, lam]]))
    return nt*lam*(1 - nt/K)

def main():
    if len(sys.argv) != 5:
        raise ValueError("Error: invalid number of command-line arguments.\nUsage: disclog <n_0> <K> <lambda> <T>")
    n0 = float(sys.argv[1])
    K = float(sys.argv[2])
    lam = float(sys.argv[3])
    T = int(sys.argv[4])
    nt = n0
    t = 0
    vals = np.zeros(shape=(T + 1,))
    vals[0] = nt
    while t < T:
        nt = ntp1(nt, K, lam)
        t += 1
        vals[t] = nt
    plt.plot(np.arange(0, T + 1, 1), vals)
    plt.show()
    print(nt)


if __name__ == "__main__":
    main()
