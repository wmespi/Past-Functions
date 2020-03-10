import json


def write_json(dictionary, outfile):
    with open(outfile, 'w') as f:
        json.dump(dictionary, f, indent = 4)
    print("Writing: ", outfile)
    return
