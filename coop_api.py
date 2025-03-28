import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from DBOperator import DBOperator

"""
// TODO
- ADD stations to sources table
    - Make sure DBOperator.add() is functioning as intended!
    - iterate through ALL of data['stations']
"""

coop_stations_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"

r = requests.get(coop_stations_url)
print(f"STATUS: {r.status_code}")
data = r.json()

# pprint(data.keys())
# Metadata
count = data['count']
units = data['units']

# for station in data['stations']:
#     pprint(station['name'])

station = data['stations']
for station in data['stations']:
    # build apis array because I'm way too lazy
    apis = []
    for product in "air_temperature wind water_temperature air_pressure humidity conductivity visibility salinity water_level hourly_height high_low daily_mean monthly_mean one_minute_water_level predictions air_gap currents currents_predictions ofs_water_level".split():
        url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={station['id']}&product={product}&datum=STND&time_zone=gmt&units=english&format=json"
        print(product)
        apis.append(url)

    apis.append(station['datums']['self']) # append with datums
    apis.append(station['notices']['self']) # start array with notices

    # Parsing CO-OP station data of last entry
    # print(f"Name: {station['name']}")
    # print(f"ID: {station['id']}")
    # print(f"State: {station['state']}")
    # print(f"\"shefcode\": {station['shefcode']}")
    # print(f"\"portscode\": {station['portscode']}")
    # print(f"Type: NOAA-{station['affiliations']}")
    # print(f"Timezone: {station['timezone']} (GMT {station['timezonecorr']})")
    # print(f"Lat,Lon: {station['lat']},{station['lng']}")
    # print(f"Disclaimers: {station['disclaimers']['self']}")
    # print(f"Notices: {station['notices']['self']}")
    # print(f"Datums: {station['datums']['self']}")
    # print(f"Forecast: {station['forecast']}")
    # print()

    entity = {
        "id": station['id'],
        "name": station['name'],
        "region": "USA",
        "type": f"NOAA-{station['affiliations']}", # Cannot be "API"
        "datums": apis, # Check if URI returns 200 or not
        # Following CANNOT BE NULL
        "timezone": f"{station['timezone']} (GMT {station['timezonecorr']})",
        "geom": f"Point({station['lng']} {station['lat']})",
    }

    pprint(entity)
    print(f"Adding entity to db...")
    # sources = DBOperator(db="capstone",table="sources")
    # sources.add(entity)
    input()

"""
^^^ ABOVE IS WHAT IS IMPORTANT
vvv BELOW IS WHAT I WANNA RUN TO PULL DATA
"""

"""
API Key:
--------------------------------
0. air temp
1. wind
2. water temp
3. air pressure
4. humidity
5. conductivity
6. visibility
7. salinity
8. water lvl
9. hr_height
10. hi/low
11. daily mean
12. montly mean
13. one min lvl
14. prediction water lvl
15. air gap (bridge and water lvl)
16. currents
17. currents prediciton
18. ofs water lvl
19. datums/disclaimers
20. notices
"""

def query(url: str) -> dict:
    response = requests.get(url)
    print(f"STATUS: {response.status_code}")
    pprint(response.json())
    return response.json()

# Meteorology
a_temp = query(apis[0])

wind = query(apis[1])

air_pressure = query(apis[3])

humidity = query(apis[4])

visibility = query(apis[6])

# Oceanography
w_temp = query(apis[2])

water_lvl = query(apis[8])

# daily_lvl_mean = query(apis[11])

monthly_lvl_mean = query(apis[12])

air_gap = query(apis[15])

currents = query(apis[16])

currents_predict = query(apis[16])

# Datums
datums = query(apis[19])

# Notice reports
notices = query(apis[20])

"""
NOTES
- Extrapolate to entire NOAA MET zone station is located in?
"""
