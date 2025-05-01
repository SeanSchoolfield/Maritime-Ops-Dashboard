import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from ...DBOperator import DBOperator

"""
// IGNORE ME! Don't think this is necessary

// Uh oh
- Noticed that a vessel's MMSI can change
    - Their IMO does not, tho
    - GFW states it's because the vessel can change AIS transmission, or
        - inconsistently transmit the same ID values
        - change owners, callsign, or transmitters
"""
def query(url: str, headers: dict) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    return response.json()

def run_update():
    GFW_TOKEN = os.environ.get("TOKEN")
    if not GFW_TOKEN:
        sys.exit("No GFW API Token provided.")

    headers = {"Authorization": f"Bearer {GFW_TOKEN}"}
    operator = DBOperator(table='vessels')

    try:
        vessels = operator.query([
            {'src': 'GFW-gfw'},
            {'src': 'GFW-AIS'},
            {'src': 'GFW-false_positives'},
            {'src': 'GFW-crowd_sourced'},
            {'src': 'GFW-dalhousie_longliner'},
        ])

        for vessel in vessels:
            mmsi = vessel.get('mmsi')
            if not mmsi:
                print("Skipping vessel without MMSI")
                continue

            vessel_url = (
                f"https://gateway.api.globalfishingwatch.org/v3/vessels/search"
                f"?query={mmsi}&datasets[0]=public-global-vessel-identity:latest"
                f"&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
            )

            result = query(vessel_url, headers)
            pprint(result)

    finally:
        operator.close()

if __name__ == "__main__":
    run_update()