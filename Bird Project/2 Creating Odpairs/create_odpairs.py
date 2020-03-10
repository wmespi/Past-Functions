import os
import sys
import json
import argparse
from datetime import datetime
import time
import itertools
from geopy.distance import distance

''' pulls all data from a folder of json files
    each json file contains all bird locations at a given timestamp
    birds are identified by their scooter id in the json file
    when a bird is in use it will not appear in any json file until the trip is over (there will be a null tag in place of its bikeid)
    bird system only updates once every 10 minutes
    any trip that starts after a timestamp (t1) and but before the system updates next (t2) will have a trip start time of t1
    any trip that ends after a timestamp (t3) and before the system updates next (t4) will have a trip end time of t4
'''

def main(infolder, outfile):
    files = find_files(infolder)
    odpairs = get_od_pairs(infolder, files)
    print(len(odpairs))
    write_json(odpairs, outfile)
    return


def get_od_pairs(infolder, files):
    odpairs = []
    scooter_locations = {}
    for f in files:
        new_locs = read_json(os.path.join(infolder, f))
        t = f[:-5]
        update_locations(odpairs, scooter_locations, new_locs,t)
    return odpairs


def update_locations(odpairs, scooter_locations, new_locs,t):
    t = new_locs['last_updated']
    for el in new_locs["data"]["bikes"]:
        bikeid = el["bike_id"]
        if bikeid == "null":
            continue
        location = (el["lat"], el["lon"])
        try:
            temp_loc = scooter_locations[bikeid][0]
            if temp_loc == location:
                scooter_locations[bikeid] = (temp_loc, t)
            if temp_loc != location:
                odpair = {}
                odpair['scooter'] = bikeid
                odpair["start_time"] = datetime.utcfromtimestamp(scooter_locations[bikeid][1]).strftime('%Y-%m-%d %H:%M:%S')
                odpair["end_time"] = datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
                odpair["origin"] = temp_loc
                odpair["destination"] = location
                odpair['distance'] = distance(temp_loc,location).meters
                odpairs.append(odpair)
                scooter_locations[bikeid] = (location, t)
        except KeyError:
            scooter_locations[bikeid] = (location, t)
            pass
    return


def find_files(mypath):
    pairs = []
    onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f)) if f.endswith('.json')]
    onlyfiles = sorted(onlyfiles, key=lambda x : float(x[:-5]))
    return onlyfiles


def read_json(filename):
    with open(filename) as json_data:
        d = json.load(json_data)
    return d


def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent=4)
    print("Writing: ", outfile)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create odpairs from bird loctiaons')
    parser.add_argument('infolder', type=str,
                    help="the bird locations folder")
    parser.add_argument('outfile', type=str,
                    help='the output file for the od pairs')
    args = parser.parse_args()
    print(args)
    main(args.infolder, args.outfile)
