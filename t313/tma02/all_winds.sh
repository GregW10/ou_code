#!/bin/bash

i=0
j=1

max=24
digs=$(printf "%.0f" $(echo "(l($max)/l(10)) + 1" | bc -l))

while (( $i < $max )); do
    j=$((i + 1))
    while (( $j <= $max )); do
        echo "$i -> $j"
        ipr=$(printf "%0${digs}d" $i)
        jpr=$(printf "%0${digs}d" $j)
        fname="windspeed_${ipr}-${jpr}.json"
        ./wind.py -q -s ${i}-${j} -o "$fname"
        shasum -a 512 -b "$fname" >> SHA512SUMS.txt
        # touch -r "$fname" "$fname.sha512"
        chmod 0400 "$fname"
        ((++j))
    done
    ((++i))
done

touch -t 200001010000.00 SHA512SUMS.txt
