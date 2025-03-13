import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps

GFW_TOKEN = os.environ.get("TOKEN")

if GFW_TOKEN == None:
    sys.exit("No GFW API Token provided.")

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}"
}

def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    pprint(response.json())
    return response.json()

"""
# Vessels
['selfReportedInfo'][0]
- callsign
- ssvid = mmsi
- flag = flag
    - Ex: "IDN", 'CHN'
- messageCounter ?
- positionsCounter ?
- sourceCode 
    - Ex: ['AIS']
- shipname = vessel_name
['combinedSourcesInfo'][0]
-'shiptypes'[0]['shiptypes'][0]['name'] = type

# Missing:
- lat,lon
- speed
- heading
- current_status
- voyage
- src
- timestamp
"""
vessels_url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search?query=mmsi&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
vessels = query(vessels_url)
# pprint(vessels['entries'][1])
# pprint(vessels.keys())

vessel = vessels['entries'][1]
mmsi = vessel['selfReportedInfo'][0]['ssvid']
vessel_url = f"https://gateway.api.globalfishingwatch.org/v3/vessels/search?query={mmsi}&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"

vessel = query(vessel_url)
# pprint(vessel['entries'])

data = {
    "datasets": [
        "public-global-fishing-events:latest",
        # "public-global-encounters-events:latest",
        "public-global-loitering-events:latest",
        "public-global-gaps-events:latest"
    ],
    # "startDate": "2025-03-09",
    # "endDate": "2025-03-10",
}

# Events for reported mmsi
events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=1"
events = requests.post(events_url, headers=headers, json=data)
print(events.status_code)
pprint(events.json()['entries'])
pprint(events.json().keys())

input()

"""
Events
- Prolly good to use these to update statuses of vessels
- Types
    - encoutners: vessel reports encounter with other vessel, risk, distance (km) and duration
    - fishing: Start/stop fishing effort
    - loitering: start/stop loiterings status
    - gaps : AIS transponder turns off/on, and gap between off-on status

- See how to update status, (lat,lon), speed, heading of matching mmsi

- Start with offset = 0, update with ['nextOffset']

# Event data
['vessel']
- flag
- name
- ssvid
- type
['position']  = lat/lon
['type'] = current_status
['regions']
- eez
- highSeas

# Metadata
['offset']
['nextOffset']
['total']

"""

