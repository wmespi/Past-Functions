import requests, json
import argparse
from geopy.distance import distance
import folium
import numpy as np


def main(outfile):
    POIs = grid(outfile)
    write_json(POIs,outfile)



def grid(outfile):
    ''' creates boundaries for gridding '''
    lower_left = [33.74837933333333,-84.40562333333332]
    upper_right = [33.789279, -84.35961499999999]
    bounds = [lower_left[0],lower_left[1],upper_right[0],upper_right[1]]
    
    print(distance(upper_right,[33.789279,-84.40562333333332])/10)
    print(distance(upper_right,[33.74837933333333,-84.35961499999999])/10)

    m = folium.Map(zoom_start = 12, location=[33.783746,-84.386330])
    grid = get_geojson_grid(upper_right, lower_left , n=8)
    pois = {}

    types = ['accounting','aquarium','apartment'
            'atm','bakery','bank','bar',
            'bus_station','cafe',
            'casino','car rental','church','condos',
            'courthouse','convenience_store','dentist','doctor',
            'embassy',
            'gas_station','gym',
            'hospital','insurance_agency','lawyer','library','liquor_store',
            'local_government_office','lodging',
            'mosque','museum',
            'park','parking','pharmacy',
            'real_estate_agency','restaurant',
            'school','shopping_mall','stadium',
            'store','subway_station','supermarket','synagogue',
            'transit_station']

    for type in types:
        kind = []
        for i, geo_json in enumerate(grid):

            # making the grid
            coords = geo_json["features"][0]["geometry"]["coordinates"]
            x,y=zip(*coords[0])
            center = [float((max(y)+min(y))/2),float((max(x)+min(x))/2)]

            # searching for all of the pois
            google(center,type,kind)
            
        pois[type] = kind
        print('poi ' + str(type) + ' done')
        try:
            print(pois[type][0])
            print(len(pois[type]))
        except IndexError:
            print(0)
            print('None')
        print('')
    return pois


def google(center,type,pois):
    ''' query that extracts pois from specific grid '''
    ##API Key
    #api_key = 'AIzaSyCtYmDTejvvIoc97QOqWcLT_BWBxhX3R4o'
    api_key = 'AIzaSyCNsLBZfKBLjPAx-DlQlGwQMKugWzTx-vM'

    ##url variable store url
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

    ##coordinate boundaries

    #bounds = 'rectangle:33.789279, -84.35961499999999|33.74837933333333,-84.40562333333332'
    center = str(center[0]) +','+ str(center[1])
    radius = str(230)

    ##POI type, can add more
    ##url with tpye classications https://developers.google.com/places/supported_types

    ##return response object
    request = url + 'location=' + center + '&radius=' + radius + '&keyword=' + type + '&key=' + api_key
    r = requests.get(request)

    ##json format data into python format
    x = r.json()

    y = x['results']

    ##store values
    for entry in y:
        print('hi')
        if type not in entry['types']:
            continue
        POI = {}
        POI['name'] = entry['name']
        POI['location'] = entry['geometry']['location']
        POI['primary_type'] = type
        POI['poi_types'] = entry['types']
        POI['vicinity'] = entry['vicinity']
        if POI in pois:
            continue
        pois.append(POI)

    return pois


def get_geojson_grid(upper_right=[-84.31360666666666,33.87107833333334], lower_left= [-84.54364833333332,33.666579999999996] , n=63):
    """Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids"
    lower_left: array_like
        The lower left hand corner of "grid of grids"
    n: integer
        The number of rows/columns in the (n,n) grid.
    Returns
    -------
    list
        List of "geojson style" dictionary objects
    """
    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            geo_json = {"type": "FeatureCollection",
                        "properties":{
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features":[]}

            grid_feature = {
                "type":"Feature",
                "geometry":{
                    "type":"Polygon",
                    "coordinates": [coordinates],
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)
    return all_boxes


##write data to file
def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent=4)
    print("Writing: ", outfile)
    return 0


##outfile to store coordinates and POIs
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot OD_Pairs')
    parser.add_argument('outfile', type=str,
                    help="the odps file")
    args = parser.parse_args()
    main(args.outfile)
