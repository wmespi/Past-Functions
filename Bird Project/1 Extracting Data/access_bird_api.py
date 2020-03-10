import os
import sys
import time
import json
import requests


def main():
    failed = 0
    for i in range(0, 10081):
        print("Iteration: ", i, " of 10081")
        start_time = time.time()
        failed += run()
        elapsed_time = time.time() - start_time
        time.sleep(60.0 - elapsed_time)
    print("Number of requests failed: \t", failed)
    return 


def run():
    failed = 0
    city_list = ["atlanta", "miami", "dallas", "los-angeles", "portland", "charlotte"]
    if not os.path.exists("data/raw/gbfs"):
        os.makedirs("data/raw/gbfs")
    for city in city_list:
        failed += run_city(city)
    return failed


def run_city(city):
    failed = 0
    folder = os.path.join("data/raw/gbfs", city)
    if not os.path.exists(folder):
        os.makedirs(folder)
    url = "https://mds.bird.co/gbfs/" + city + "/free_bikes"
    r = requests.get(url)
    if r != None and r.status_code == 200:
        response = json.loads(r.text)
        t = time.time()
        t_str = os.path.join(folder, str(t) + ".json")
        with open(t_str, 'w') as f:
            json.dump(response, f, indent=4)
    else:
        failed += 1
    return failed


if __name__ == "__main__":
    main()
