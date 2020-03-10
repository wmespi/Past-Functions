import pandas as pd
import numpy as np
import itertools
from datetime import datetime,timedelta
from geopy.distance import distance
from scipy import spatial
import operator
import math



def kd_tree(points,paths):

    ''' pull all coordinates from POI list and create nearest neighbor tree '''
    tree = spatial.KDTree(points


    ''' find the nearest neighbor POI for each origin/destination '''

    for i,origin in enumerate(paths):
        o_tup = tree.query(origin)

        o_filter = poi_list[o_tup[1]]

        o_poi = [o_filter['location']['lat'],o_filter['location']['lng']]


        ''' calculate distance between path and POI '''

        o_dist = distance(path['origin'],o_poi).meters

    return paths
