import json
import pandas as pd
import numpy as np
import argparse
import itertools
from datetime import datetime,timedelta
from geopy.distance import distance
from scipy import spatial
import operator
import math


def main(infile1,infile2,outfile):
    odps = read_json(infile1)
    pois = read_json(infile2)
    get_associations(pois,odps,outfile)


def cartesian(coords,elevation=0):
    latitude = coords[0] * (math.pi / 180)
    longitude = coords[1] * (math.pi / 180)

    R = 6371 # 6378137.0 + elevation  # relative to centre of the earth
    X = R * math.cos(latitude) * math.cos(longitude)
    Y = R * math.cos(latitude) * math.sin(longitude)
    Z = R * math.sin(latitude)
    return [X, Y, Z]


def get_associations(pois,paths,outfile):
    ''' create new list that holds all the POIs '''

    poi_list = []
    for key in pois.keys():
        for i in pois[key]:
            poi_list.append(i)


    ''' pull all coordinates from POI list and create nearest neighbor tree '''
    ## convert
    poi_locs = [cartesian([x['location']['lat'],x['location']['lng']]) for x in poi_list]
    tree = spatial.KDTree(poi_locs)


    ''' find the nearest neighbor POI for each origin/destination '''

    for i,path in enumerate(paths):
        ''' nearest neighbor query '''
        origin = cartesian(path['origin'])
        destination = cartesian(path['destination'])

        o_tup = tree.query(origin)
        d_tup = tree.query(destination)


        ''' closest POI for origin/destination '''

        o_filter = poi_list[o_tup[1]]
        d_filter = poi_list[d_tup[1]]

        o_poi = [o_filter['location']['lat'],o_filter['location']['lng']]
        d_poi = [d_filter['location']['lat'],d_filter['location']['lng']]


        ''' check to see if origin and destination are the same poi, if so requery for the origin because destination is more likely to be accurate out of the two '''
        if o_filter['name'] == d_filter['name']:
            poi_list2 = poi_list[:]
            poi_list2.remove(o_filter)
            poi_locs2 = [cartesian([x['location']['lat'],x['location']['lng']]) for x in poi_list2]
            tree2 = spatial.KDTree(poi_locs2)
            o_tup = tree2.query(origin)
            o_filter = poi_list2[o_tup[1]]
            o_poi = [o_filter['location']['lat'],o_filter['location']['lng']]
            


        ''' calculate distance between path and POI '''

        o_dist = distance(path['origin'],o_poi).meters
        d_dist = distance(path['destination'],d_poi).meters


        ''' input information into path data strucuture '''

        paths[i]['POI distance from origin'] = o_dist
        paths[i]['POI associated with origin'] = o_filter
        paths[i]['POI distance from destination'] = d_dist
        paths[i]['POI associated with destination'] = d_filter

        if i%100==0:
            print("path " + str(i) + " done")


    write_json(paths,outfile)
    return paths


def read_json(file):
    odpairs = []
    with open(file) as json_data:
        d = json.load(json_data)
    odpairs = d
    return odpairs

def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent = 4)
    print("Writing: ", outfile)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot OD_Pairs')
    parser.add_argument('infile1', type=str,
                    help="the odps file")
    parser.add_argument('infile2', type=str,
                    help="the pois file")
    parser.add_argument('outfile', type=str,
                    help='the output file for the od pairs')
    args = parser.parse_args()
    print(args)
    main(args.infile1,args.infile2, args.outfile)
