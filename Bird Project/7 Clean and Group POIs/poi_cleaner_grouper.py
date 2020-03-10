import argparse
import json
import itertools

## pre cleaning 4420 pois
## post cleaning 2526 pois

def main(infile,outfile):
    raw = read_json(infile)
    cleaned_pois = cleaner(raw)
    grouped_pois = make_dict(cleaned_pois)
    write_json(grouped_pois,outfile)


def make_dict(list_pois):
    ## initialize final dictionary
    dict_pois = {}
    print(len(list_pois))

    groups = ['business','public_transit','hotel','recreation','shopping','parking','food','residential','health','multiple']
    count = 0
    for group in groups:
        dict_pois[group] = list(filter(lambda k: k['overall_group'] == group,list_pois))
        print(len(dict_pois[group]))
        count += len(dict_pois[group])
    print(count)
    return dict_pois


def cleaner(raw):
    ## cleaned the pois, make sure if there are pois with the same location, they are accounted for
    cleaned_pois = {}
    cleaned_pois['multiple'] = []
    coords = []
    types = []

    ## poi types that do not have their top poi_type entry matching their primary type
    exceptions = ['apartment','condo']

    ## read through all pois, do first round of cleaning, and store all the unique locations
    temp = []
    coords = []
    for type in raw.keys(): ## temporary dictionary for cleaned pois for each type
        for entry in raw[type]:

            ## skip pois where google does not know location
            if entry['vicinity'] == 'Atlanta':
                continue

            ## make sure all pois match their type of highest priority
            ptype = entry['primary_type']
            if type in exceptions:
                test = entry['poi_types'][len(entry['poi_types']) -1]
            else:
                test = entry['poi_types'][0]
            if ptype != test:
                continue

            ## keep track of all unique locations
            loc = entry['location']
            if loc not in coords:
                coords.append(loc)
            temp.append(entry)

    ## either assign multiple tag or see if it's the same location
    print(len(temp))
    multiple = assign_tags(temp,coords)

    return multiple


def assign_tags(temp,coords):
    i = 0

    ## find all pois with the same coordinates and keep track of duplicates
    extras = []
    fixed = []
    for coord in coords:
        same = list(filter(lambda k: k['location'] == coord, temp))

        ## for all of the pois that have a unique location
        if len(same) == 1:
            new_poi = group(same)
            fixed.append(new_poi)
            continue

        ## list of list of pois that shar the same location
        extras.append(same)

    ## get rid of duplicates and replace with one POI
    for dupl_list in extras:

        ## sort and group them by pairs to see if there are multiple different pois
        name_sort = sorted(dupl_list, key = lambda k: k['name'])
        name_group = [list(g) for _,g in itertools.groupby(name_sort, key = lambda k: k['name'])]

        ## all items in dupl_list have the same name so assume same location
        if len(name_group) ==1:
            new_poi = group(name_group[0])
            fixed.append(new_poi)
        ## there are multiple different pois in dupl_list, check if they are in the same type or group
        ## if not, assign multiple
        else:
            new_poi = group(dupl_list)
            fixed.append(new_poi)

    return fixed


def group(dupl_list):
    ## poi groups
    groups = {}
    groups['business'] = ['accounting', 'bank', 'business', 'car_rental', 'embassy', 'insurance_agency', 'lawyer', 'local_government_office', 'real_estate_agency', 'school']
    groups['public_transit'] = ['subway_station', 'transit_station']
    groups['hotel'] = ['lodging']
    groups['recreation'] = ['aquarium', 'bar', 'casino', 'church', 'library', 'mosque', 'museum', 'park', 'stadium', 'synagogue']
    groups['shopping'] = ['convenience_store', 'gas_station', 'liquor_store', 'shopping_mall']
    groups['parking'] = ['parking']
    groups['food'] = ['bakery', 'cafe', 'restaurant', 'supermarket']
    groups['residential'] = ['apartment', 'condo', 'neighborhood']
    groups['health'] = ['dentist', 'doctor', 'gym', 'hospital', 'pharmacy']
    groups['multiple'] = ['multiple']

    group_color = {}
    group_color['business'] = 'green'
    group_color['public_transit'] = 'orange'
    group_color['hotel'] = 'black'
    group_color['recreation'] = 'purple'
    group_color['shopping'] = 'darkgreen'
    group_color['parking'] = 'blue'
    group_color['food'] = 'red'
    group_color['residential'] = 'beige'
    group_color['health'] = 'white'
    group_color['multiple'] = 'gray'

    poi = {}

    ## check to see how many different types there are
    type_sort = sorted(dupl_list, key = lambda k: k['primary_type'])
    type_group = [list(g) for _,g in itertools.groupby(dupl_list, key = lambda k: k['primary_type'])]

    ## check to see if the different pois all have the same primary type
    if len(type_group) == 1:
        poi = type_group[0][0]
        poi['name'] = poi['name'] + ' (multiple locations with same primary type)'

        ##assign overall_group
        for group in groups.keys():
            if poi['primary_type'] in groups[group]:
                poi['overall_group'] = group
                poi['group_color'] = group_color[group]

    else:
        types = [i[0]['primary_type'] for i in type_group]
        poi = type_group[0][0]
        poi['name'] = poi['name'] + ' (multiple locations with diff primary type)'

        for group in groups.keys():

            ## check to see if the all the pois primary types are in the same group
            check = [i for i in types if i in groups[group]]
            success = 0
            if len(check) == len(types):
                poi['overall_group'] = group
                poi['group_color'] = group_color[group]
                poi['primary_type'] = 'similar'
                success += 1

        if success == 0:
            poi['overall_group'] = 'multiple'
            poi['primary_type'] = 'multiple'
            poi['group_color'] = group_color['multiple']

    return poi


def read_json(file):
    odpairs = []
    with open(file) as json_data:
        d = json.load(json_data)
    odpairs = d
    return odpairs


def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent=4)
    print("Writing: ", outfile)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot OD_Pairs')
    parser.add_argument('infile', type=str,
                    help="the odps file")
    parser.add_argument('outfile', type=str,
                    help="the odps file")
    args = parser.parse_args()
    main(args.infile,args.outfile)
