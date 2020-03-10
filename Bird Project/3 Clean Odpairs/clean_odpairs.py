from geopy.distance import distance
import argparse
import json
import time
from datetime import datetime,timedelta
import itertools

# cleaned odpairs based on trips greater than 75 meters
# and less than 3000 meters
# start time after 7 am and before 9pm
# end time after 7 am and before 9 pm
# trip duration should be less than 1.5 hours

started = time.time()

def main(infile, outfile):
    print('start:',started-started)
    odpairs = read_json(infile)
    #cleaned_odps = clean_pairs(odpairs)
    #write_json(cleaned_odps,outfile)
    return


def read_json(file):
    odpairs = []
    with open(file) as json_data:
        d = json.load(json_data)
    odpairs = d
    print(len(odpairs))
    count5 = 0
    count10 = 0
    count20 = 0
    for i,pair in enumerate(odpairs):
        if pair['distance'] <= 5:
            count5 +=1
        if pair['distance'] <= 10:
            count10 += 1
        if pair['distance'] <= 20:
            count20 += 1
        if i%1000 == 0:
            print(i)
    print('Total Trips Under 5 m: ' +str(count5))
    print('Total Trips Under 10 m: ' +str(count10))
    print('Total Trips Under 20 m: ' +str(count20))
    print('file read:',time.time()-started)
    return odpairs


def clean_pairs(odpairs):
    ''' get list of cleaned odpairs for entire city of atlanta '''
    cleaned_odps = list(filter(lambda k: distance(k['origin'], k['destination']).meters >= 75
                                and distance(k['origin'], k['destination']).meters <= 3000
                                and datetime.strptime(k['start_time'], '%Y-%m-%d %H:%M:%S').hour >= 7
                                and datetime.strptime(k['start_time'], '%Y-%m-%d %H:%M:%S').hour < 21
                                and datetime.strptime(k['end_time'], '%Y-%m-%d %H:%M:%S').hour <= 21
                                and datetime.strptime(k['end_time'], '%Y-%m-%d %H:%M:%S').hour >= 7
                                and ( datetime.strptime(k['end_time'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(k['start_time'], '%Y-%m-%d %H:%M:%S') ).total_seconds() / 3600 <= 1.5,
                                odpairs))
    ''' further clean list of odpairs to grid of highest traffic '''
    ## coordinates were found from gridding city of atlanta and isolating grid with most of the traffic
    ## makes google queries much easier/cost effective
    ## 72.4% of all trips occured in this one grid point of the city
    lower_left = [33.74837933333333,-84.40562333333332]
    upper_right = [33.789279, -84.35961499999999]
    grid13_odps = list(filter(lambda k: k['origin'][0] >= lower_left[0] and
                                   k['origin'][1] >= lower_left[1] and
                                   k['origin'][0] <= upper_right[0] and
                                   k['origin'][1] <= upper_right[1] and
                                   k['destination'][0] >= lower_left[0] and
                                   k['destination'][1] >= lower_left[1] and
                                   k['destination'][0] <= upper_right[0] and
                                   k['destination'][1] <= upper_right[1],
                                   cleaned_odps))
    print('odps cleaned:', time.time()-started)
    print('odps for all of Atlanta: ' + str(len(cleaned_odps)))
    print('odps for grid 13: ' + str(len(grid13_odps)))
    return grid13_odps


def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent=4)
    print("Writing: ", outfile)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot OD_Pairs')
    parser.add_argument('infolder', type=str,
                    help="the odps folder")
    parser.add_argument('outfile', type=str,
                    help='the output file for the od pairs')
    args = parser.parse_args()
    print(args)
    main(args.infolder, args.outfile)
