#!/usr/bin/python3

import math


def deg_to_rad(deg):
    return math.pi*deg/180


def rad_to_deg(rad):
    return rad*180/math.pi


def hour_angle_at_elevation(a, phi, delta):
    # I will assume the parameters are passed in in degrees
    z = deg_to_rad(90 - a)
    phi = deg_to_rad(phi)
    delta = deg_to_rad(delta)
    print(z, phi, delta)
    print((math.cos(z) - math.sin(phi)*math.sin(delta))/(math.cos(phi)*math.cos(delta)))
    return rad_to_deg(math.acos((math.cos(z) - math.sin(phi)*math.sin(delta))/(math.cos(phi)*math.cos(delta))))


eqx_height = 40 # degrees
lat = 90 - eqx_height # degrees
rot_rate = 15 # deg/hour
declination = 0 # degrees (since it is the equinox)

obliquity = 23.44 # Earth's current obliquity (degrees)


def main():
    print("Question a")
    building_height = 15 # degrees
    h_angle = hour_angle_at_elevation(building_height, lat, declination)
    print(f"Hour angle when sun gets hidden again by building before sunset: {h_angle} deg")
    time_hidden = 1 + (90 - h_angle)/rot_rate # total time the sun is hidden during the day
    print(f"Time hidden: {time_hidden} h")
    time_visible = 12 - time_hidden
    print(f"Total time visible: {time_visible} h")

    print("Question b")
    midsummer_height = eqx_height - obliquity
    midwinter_height = eqx_height + obliquity
    print(f"Midsummer height: {midsummer_height} deg\nMidwinter height: {midwinter_height} deg")
    

if __name__ == "__main__":
    main()

