import json


def read_json(file):
    with open(file) as json_data:
        d = json.load(json_data)
    return d
