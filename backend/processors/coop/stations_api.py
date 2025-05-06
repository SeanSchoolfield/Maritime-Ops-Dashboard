import requests
import csv
from pprint import pprint
from json import dumps
from time import sleep
from ...DBOperator import DBOperator

COOP_STATIONS_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
ALL_PRODUCTS = (
    "air_temperature wind water_temperature air_pressure humidity conductivity "
    "visibility salinity water_level hourly_height high_low daily_mean monthly_mean "
    "one_minute_water_level predictions air_gap currents currents_predictions ofs_water_level"
).split()

def _fetch_available_datums(station_id: str, http_get=requests.get) -> list[str]:
    available = []
    for product in ALL_PRODUCTS:
        url = (
            f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
            f"date=latest&station={station_id}&product={product}&datum=STND&"
            f"time_zone=gmt&units=english&format=json"
        )
        resp = http_get(url)
        if resp.status_code == 200:
            j = resp.json()
            if "error" not in j:
                available.append(product)
    return available

def run(
    DBOperatorClass=DBOperator,
    http_get=requests.get,
    sleep_fn: callable = sleep,
) -> tuple[list[dict], list[dict]]:
    """
    Fetch all NOAA-COOP stations, probe their available datums, build station entities,
    insert into Postgres via DBOperator, and return (inserted, failures).
    """
    sources_db = DBOperatorClass(table="sources")
    inserted = []
    failures = []

    resp = http_get(COOP_STATIONS_URL)
    if resp.status_code != 200:
        sources_db.close()
        raise RuntimeError(f"Failed to fetch stations: HTTP {resp.status_code}")
    stations = resp.json().get("stations", [])

    for st in stations:
        sid = st["id"]
        products = _fetch_available_datums(sid, http_get)

        entity = {
            "id":        sid,
            "name":      st.get("name"),
            "region":    st.get("state", "USA"),
            "type":      "NOAA-COOP",
            "datums":    products,
            "timezone":  f"{st.get('timezone')} (GMT {st.get('timezonecorr')})",
            "geom":      f"Point({st.get('lng')} {st.get('lat')})",
        }

        try:
            sources_db.add(entity.copy())
            sources_db.commit()
            inserted.append(entity)
        except Exception as e:
            pprint(f"Error inserting station {sid}: {e}")
            sources_db.rollback()
            failures.append(entity)

        sleep_fn(0.1)

    sources_db.close()
    return inserted, failures


if __name__ == "__main__":
    ins, fails = run()
    print(f"Inserted {len(ins)} stations")
    if fails:
        with open("coop-station-failures.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fails[0].keys())
            w.writeheader()
            w.writerows(fails)
        print(f"Wrote {len(fails)} failures to coop-station-failures.csv")
