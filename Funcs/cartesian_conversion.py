import pandas as pd
import numpy as np
import itertools
from datetime import datetime,timedelta
from geopy.distance import distance
from scipy import spatial
import operator
import math



def cartesian(coords,elevation=0):
    latitude = coords[0] * (math.pi / 180)
    longitude = coords[1] * (math.pi / 180)

    R = 6371 # 6378137.0 + elevation  # relative to centre of the earth
    X = R * math.cos(latitude) * math.cos(longitude)
    Y = R * math.cos(latitude) * math.sin(longitude)
    Z = R * math.sin(latitude)
    return [X, Y, Z]
