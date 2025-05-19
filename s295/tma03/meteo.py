#!/usr/bin/env python3

import meteostat as ms
import datetime

park = (50.8419667, 4.3870201)


def main():
    point = ms.Point(park[0], park[1])
    daily = ms.Daily(point,
                     datetime.datetime(2025, 4, 25),
                     datetime.datetime(2025, 5,  5))
    # print(daily.stations)
    station = ms.Stations().nearby(park[0], park[1]).fetch(1)
    station.to_csv("station.csv")
    data = daily.fetch()
    print(data)
    data.to_csv("weather-data.csv")


if __name__ == "__main__":
    main()

# nonce=756530048
