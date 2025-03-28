from DBOperator import DBOperator
import csv
import requests
from time import sleep
from pprint import pprint
from json import loads, dumps

zones_url = "https://api.weather.gov/zones"
zones = requests.get(zones_url)

print(f"STATUS: {zones.status_code}")

data = zones.json()['features']

zone_types = []

# TODO:
# - Search through failures csv to see if any zoneIDs do NOT exist in DB
#   - Seems like there are duplicates with type="PUBLIC"

table = DBOperator(table='zones')
dubs = 0
els = 0

for zone in data:
    # pprint(zone)
    entity = {}
    # print(f"ZoneID: {zone['properties']['id']}")
    entity['id'] = zone['properties']['id']
    # print(f"Zone Name: {zone['properties']['name']}")
    entity['name'] = zone['properties']['name']
    # print(f"Timezone: {zone['properties']['timeZone'][0]}")
    # entity['timezone'] = zone['properties']['timeZone'][0]
    # print(f"Region: US-{zone['properties']['state']}")
    entity['region'] = f"USA-{zone['properties']['state']}"
    # print(f"Zone type: {zone['properties']['type'].upper()}")
    if zone['properties']['type'].upper() not in zone_types:
        zone_types.append(zone['properties']['type'].upper())
    entity['type'] = zone['properties']['type'].upper()
    # print(f"Source ID: {zone['properties']['gridIdentifier']}")
    entity['src_id'] = zone['properties']['gridIdentifier']
    forecast_url = zone['properties']['forecastOffice']
    # print(f"Forecast office URI: {forecast_url}")
    # print()
    # Retrieving zone geometry
    # print("Geometry:") # TODO: How to format into GeogFromText(Polygon())
    zone = requests.get(zone['properties']['@id'])
    # print(f"STATUS: {zone.status_code}")
    entity['geom'] = zone.json()['geometry']

    # pprint(entity)
    try:
        # Add to zones table
        # print("Adding to Zones...")
        table.add(entity)
        table.commit()
        dubs += 1
    except Exception as e:
        els += 1
        table.rollback()
        print(f"{e}\nError adding to zones...")
        with open('zones_failures.csv', 'a', newline='') as outFile:
            writer = csv.DictWriter(outFile, delimiter=',', fieldnames=entity.keys())
            writer.writerow(entity)
    finally:
        sleep(0.1)

print(f'{len(data)} zones identified')
print(f"{dubs} zones added to DB")
print(f"{els} zones failed were not added to DB")
table.close()



















