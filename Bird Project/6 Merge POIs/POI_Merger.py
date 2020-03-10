import argparse
import json

def main(infile1,infile2,outfile):
    a = read_json(infile1)
    print(len(a))
    b = read_json(infile2)

    for key in b.keys():
        if key in a.keys():
            for item in b[key]:
                a[key].append(item)
        else:
            a[key] = b[key]
            print(key)
            print((a[key]))

    c = {}

    types = ['accounting','aquarium','apartment',
            'bakery','bank','bar','business'
            'cafe',
            'casino','condo','car_rental','church',
            'convenience_store','dentist','doctor',
            'embassy',
            'gas_station','gym',
            'hospital','insurance_agency','lawyer','library','liquor_store',
            'local_government_office','lodging',
            'mosque','museum',
            'park','parking','pharmacy',
            'real_estate_agency','restaurant',
            'school','shopping_mall','stadium',
            'subway_station','supermarket','synagogue',
            'transit_station','neighborhood']

    for key in a.keys():
        if key not in types:
            print(key)
            continue
        c[key] = a[key]
    print(c.keys())
    write_json(c,outfile)

def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent=4)
    print("Writing: ", outfile)
    return 0


def read_json(file):
    odpairs = []
    with open(file) as json_data:
        d = json.load(json_data)
    odpairs = d
    return odpairs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot OD_Pairs')
    parser.add_argument('infile1', type=str,
                    help="the odps file")
    parser.add_argument('infile2', type=str,
                    help="the odps file")
    parser.add_argument('outfile', type=str,
                    help="the odps file")
    args = parser.parse_args()
    main(args.infile1,args.infile2,args.outfile)

# , 'Midtown Homes', 'Old Fourth Ward Homes', 'Virginia Highlands Homes',
# 'Marta', 'Five Points', 'King Memorial Transit Station', 'Dome/GWCC/Philips Arena/CNN Center Transit Station', 'Civic Center Station',
# 'North Avenue Marta Station', 'Peachtree Center Transit Station', 'Midtown Marta', 'Arts Center', 'Georgia State Marta', 'Vine City Marta']
