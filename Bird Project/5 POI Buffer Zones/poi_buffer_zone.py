from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point
import json
import argparse


proj_wgs84 = pyproj.Proj(init='epsg:4326')

''' infile is the file of cleaned ungrouped POIs '''
''' outfile is a small file of children POIs and their locations in dictionaries with the keys being the name of the parent POI '''

def main(infile, outfile):
    print('##########################')
    pois = read_json(infile)
    print('##########################')
    limited_pois = limit(pois)
    print('##########################')
    buffered_pois = create_buffers(limited_pois)
    print('##########################')
    write_json(buffered_pois, outfile)
    print('##########################')
    #print(buffered_pois)


def create_buffers(pois):
    buffered_pois = {}
    for poi in pois:
        temp = []
        print(poi)
        lat = poi['location']['lat']
        lon = poi['location']['lng']
        if(poi['name'] == 'Georgia Aquarium'):
            km = 0.09
            i_d = 8

        elif(poi['primary_type'] == 'neighborhood'):
            km = 0.14
            i_d = 8
            km1 = .29
            i_d1 = 4

            kid_poi_coords1 = geodesic_point_buffer(lat,lon,km1)
            for i,coord in enumerate(kid_poi_coords1):
                if i% i_d1 != 0:
                    continue
                poi_count += 1
                kid_poi = {}
                kid_poi['location'] = {}
                kid_poi['name'] = poi['name'] + ' ' + str(i)
                kid_poi['location']['lat'] = coord[1]
                kid_poi['location']['lng'] = coord[0]
                kid_poi['primary_type'] = poi['primary_type']
                kid_poi['poi_types'] = poi['poi_types']
                kid_poi['vicinity'] = poi['vicinity']
                temp.append(kid_poi)

        if poi['name'] in ['Five Points', 'King Memorial Transit Station', 'Dome/GWCC/Philips Arena/CNN Center Transit Station', 'Civic Center Station', 'North Avenue Marta Station', 'Peachtree Center Transit Station', 'Midtown Marta', 'Arts Center', 'Georgia State Marta', 'Vine City Marta', 'Garnett Transit Station']:
            km = 0.02
            i_d = 8

        else:
            km = .14
            i_d = 8

        kid_poi_coords = geodesic_point_buffer(lat,lon,km)

        poi_count = 0

        ''' now creates a dictionary of lists of the children POIs with keys that are the name of the parent POI '''

        for i,coord in enumerate(kid_poi_coords):
            if i% i_d != 0:
                continue
            poi_count += 1
            kid_poi = {}
            kid_poi['location'] = {}
            kid_poi['name'] = poi['name'] + ' ' + str(i)
            kid_poi['location']['lat'] = coord[1]
            kid_poi['location']['lng'] = coord[0]
            kid_poi['primary_type'] = poi['primary_type']
            kid_poi['poi_types'] = poi['poi_types']
            kid_poi['vicinity'] = poi['vicinity']
            temp.append(kid_poi)


        buffered_pois[poi['primary_type']] = temp
        print(poi_count)
    return buffered_pois


def geodesic_point_buffer(lat, lon, km):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(project, buf).exterior.coords[:]

''' limits the POIs considered for childred POIs to only ones we want, which here is only Mercedes-Benz and the Aquarium '''

def limit(groups):
    temp = []
    for key in groups.keys():
        for poi in groups[key]:
            ''' older POIs that needed kid pois below '''
            ''' 'Mercedes-Benz Stadium','Georgia Aquarium', 'Midtown Homes', 'Old Fourth Ward Homes', 'Virginia Highlands Homes' '''
            if(poi['name'] in ['Five Points', 'King Memorial Transit Station', 'Dome/GWCC/Philips Arena/CNN Center Transit Station', 'Civic Center Station', 'North Avenue Marta Station', 'Peachtree Center Marta', 'Midtown Marta', 'Arts Center', 'Georgia State Marta', 'Vine City Marta', 'Garnett Transit Station'] and poi['primary_type'] in ['subway_station']):
                temp.append(poi)
            if(poi['primary_type'] == 'neighborhood'):
                temp.append(poi)
            if(poi['name'] == 'Georgia Aquarium'):
                temp.append(poi)
            if(poi['name'] == 'Mercedes-Benz Stadium'):
                temp.append(poi)
    return temp

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
    parser.add_argument('infile', type=str,
                    help="the pois file")
    parser.add_argument('outfile', type=str,
                    help='the output file for the pois with buffer')
    args = parser.parse_args()
    print(args)
    main(args.infile, args.outfile)
