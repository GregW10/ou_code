import math
import numpy as np

# constant definitions

Wh  = 3_600 # (J) number of joules in a Watt-hour
kWh = Wh*1_000 # (J)
MWh = Wh*1_000_000 # (J)
GWh = Wh*1_000_000_000 # (J)
TWh = Wh*1_000_000_000_000 # (J)


# functions

def dec_latlong_to_sex_latlong(latlong: float, rel_tol: float = 1e-9) -> tuple:
    if not isinstance(latlong, float):
        raise TypeError("Error: expected float.")
    mult = 1
    if latlong < 0:
        mult = -1
        latlong *= -1
    degrees = float(math.floor(latlong))
    actual_minutes = (latlong - degrees)*60
    minutes = math.floor(actual_minutes)
    seconds = (actual_minutes - minutes)*60
    return (mult*degrees, minutes + 1, 0.0) if math.isclose(seconds, 60, rel_tol=rel_tol) else (mult*degrees, minutes, seconds)






