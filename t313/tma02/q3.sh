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
    alias echo="echo -e"
fi

if [ $# -lt 2 ]; then
    echo "${red}Error: insufficient command-line arguments."
    exit 1
fi

rate=$1

vals=("$@")

n=0

sum=0

for val in "${vals[@]:1}"; do
    pv="$(echo "$val/((1 + $rate)^$n)" | bc -l)"
    printf "%.2f\n" "$pv"
    sum="$(echo "$sum + $pv" | bc -l)"
    ((++n))
done

printf "\n%.2f\n" "$sum"


