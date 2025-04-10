import os
import sys
import csv
import requests
from pprint import pprint
from datetime import datetime
from json import loads, dumps
from DBOperator import DBOperator

# WARNING: Currently have 1206 entities in Vessels, and it's making the app LAG TF OUT!
"""
// TODO

Algoritm:
- Run Me!
- When I error:
    - If I error out on row 2, see how many rows already exist in DB, up until a row doesn't
    - If I don't error out on row 2, delete all rows up until row that errors out
"""
dubs = 0
vessels = DBOperator(db="capstone",table="vessels")

failures = []

def convert_status(var):
        if var in "1".split(',') or var == "anchored":
            return "ANCHORED"
        elif var in "2".split(','):
            return "UNMANNED"
        elif var in "3,4".split(','):
            return "LIMITED MOVEMENT"
        elif var in "5".split(','):
            return "MOORED"
        elif var in "6".split(','):
            return "AGROUND"
        elif var in "7".split(','):
            return "FISHING"
        elif var in "0,8".split(','):
            return "UNDERWAY"
        elif var in "9,10".split(','):
            return "HAZARDOUS CARGO"
        elif var in "11,12".split(','):
            return "IN TOW"
        elif var in "14".split(','):
            return "EMERGENCY"
        else:
            return "UNKNOWN"

cadastre='MarineCadastre_2024-12-30/AIS_2024_09_30.csv'

# Converting NAIS AIS ship identifier codes into our own vessel types
cargo = [i for i in range(70, 80)] + [1003, 1004, 1016]
fishing = [30, 1001, 1002]
tanker = [i for i in range(80, 90)] + [1017, 1024]
tug = [21, 22, 31, 32, 52, 1023, 1025]
passenger = [i for i in range(60,70)] + [1012, 1013, 1014, 1015]
recreational = [36, 37, 1019]
with open(cadastre, newline='') as inFile:
    data = csv.reader(inFile, delimiter=',')
    headers = next(data, None)
    for row in data:
        vessel = {}
        vessel['mmsi'] = int(float(row[0])) # mmsi
        vessel['geom'] = f"Point({row[4]} {row[3]})"
        if len(row[7]) == 0:
            vessel['vessel_name'] = "UNKNOWN"
        else:
            vessel['vessel_name'] = row[7]
        vessel['callsign'] = row[9]
        vessel['timestamp'] = row[1] # UTC datetime
        if len(row[5]) > 0:
            vessel['heading'] = round(float(row[5]), 2) # heading over ground degrees
        else:
            vessel['heading'] = 0.0
        # vessel['heading'] = row[6] # true heading degrees
        if len(row[4]) > 0:
            vessel['speed'] = round(float(row[4]), 2) # knots
        else:
            vessel['speed'] = 0.0
        vessel['current_status'] = convert_status(row[11])
        # print("voyage")
        vessel['src'] = "MarineCadastre-AIS"
        # converging NAIS specs to TYPE
        if len(row[10]) > 0:
            ais_code = int(row[10])
            if ais_code in cargo:
                vessel['type'] = "CARGO"
            elif ais_code in fishing:
                vessel['type'] = "FISHING"
            elif ais_code in tanker:
                vessel['type'] = "TANKER"
            elif ais_code in tug:
                vessel['type'] = "TUG"
            elif ais_code in passenger:
                vessel['type'] = "PASSENGER"
            elif ais_code in recreational:
                vessel['type'] = "RECREATIONAL"
        else:
            vessel['type'] = "OTHER"
        vessel['flag'] = "USA"
        if len(row[12]) > 0:
            vessel['length'] = round(float(row[12]), 2) # meters
        else:
            vessel['length'] = 0.0
        if len(row[13]) > 0:
            vessel['width'] = round(float(row[13]), 2) # meters
        else:
            vessel['width'] = 0.0
        if len(row[14]) > 0:
            vessel['draft'] = round(float(row[14]), 2) # meters
        else:
            vessel['draft'] = 0.0
        if len(row[15]) > 0:
            vessel['cargo_weight'] = round(float(row[15]), 2)
        else:
            vessel['cargo_weight'] = 0.0
        if len(row[2]) > 0:
            vessel['lat'] = round(float(row[2]), 2)
        else:
            vessel['lat'] = 0.0
        if len(row[3]) > 0:
            vessel['lon'] = round(float(row[3]), 2)
        else:
            vessel['lon'] = 0.0
        vessel['dist_from_port'] = 0.0
        vessel['dist_from_shore'] = 0.0
        # print(f"IMO: {row[8]}") # International Maritime Organization Vessel number
        # print(f"tranciever class: {row[16]}") # AIS tranciever class

        try:
            # I forgot python doesn't treat parameters as local variables, so I
            # was REALLY confused why this kept losing its geometry element
            # during debugging... So I did this
            vessels.add(vessel.copy())
            vessels.commit()
            dubs += 1
        except Exception as e:
            print(f"An error occured adding vessel to DB...\n{e}")
            print("This vessel caused the failure:")
            pprint(vessel)
            input()

            failures.append(vessel)

print(f"{dubs} total pushes to DB.")
print(f"{len(failures)} total vessels that weren't added to DB for some reason")

# TODO: DUNNO IF THE FOLLOWING ACCURATELY SAVES DATA
with open('failures.csv','w',newline='') as outFile:
    writer = csv.DictWriter(outFile, delimiter=',', fieldnames=failures[0].keys())
    writer.writeheader()
    for goob in failures:
        writer.writerow(goob)

vessels.close()
