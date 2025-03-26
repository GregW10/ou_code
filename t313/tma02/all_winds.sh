#!/bin/bash

i=0
j=1

max=24

while (( $i < $max )); do
    j=$((i + 1))
    while (( $j <= $max )); do
        echo "$i -> $j"
        fname="windspeed_${i}-${j}.json"
        ./wind.py -q -s ${i}-${j} -o "$fname"
        shasum -a 512 -b "$fname" >> SHA512SUMS.txt
        # touch -r "$fname" "$fname.sha512"
        chmod 0400 "$fname"
        ((++j))
    done
    ((++i))
done

touch -t 200001010000.00 SHA512SUMS.txt
