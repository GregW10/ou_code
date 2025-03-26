#!/bin/bash

red=""
green=""
blue=""
bold=""
reset=""

if [ -t 1 ] && [ -t 2 ]; then
    red="\033[38;5;9m"
    green="\033[38;5;10m"
    blue="\033[38;5;12m"
    bold="\033[38;5;1m"
    reset="\033[38;5;0m"
fi

if [ $# -lt 2 ]; then
    echo -e "${red}Error: insufficient command-line arguments."
    exit 1
fi

rate=0.05
sig=4

vals=()

for val in "$@"; do
	if [[ "$val" == rate=* ]]; then
		rate="$(echo -e "$val" | awk -F'=' '{ print $2 '})"
		continue
	elif [[ "$val" == sig=* ]]; then
		sig="$(echo -e "$val" | awk -F'=' '{ print $2 '})"
		continue
	fi
	vals+=("$val")
done

n=0

sum=0

for val in "${vals[@]}"; do
    pv="$(echo -e "$val/((1 + $rate)^$n)" | bc -l)"
    printf "%.${sig}g\n" "$pv"
    sum="$(echo -e "$sum + $pv" | bc -l)"
    ((++n))
done

printf "\n%.${sig}g\n" "$sum"

