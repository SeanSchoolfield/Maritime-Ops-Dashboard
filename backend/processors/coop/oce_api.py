import csv
import requests
from datetime import datetime, timezone
from pprint import pprint
from time import sleep
from ...DBOperator import DBOperator


def request(id, product):
    url = (
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
        f"?date=latest&station={id}&product={product}&datum=STND"
        f"&time_zone=gmt&units=english&format=json"
    )
    res = requests.get(url)
    if res.status_code >= 400:
        return res
    return res.json()


def run(DBOperatorClass=DBOperator, sleep_fn=sleep):

    source_db = DBOperatorClass(table='sources')
    stations = source_db.query([{'type': 'NOAA-COOP'}])
    source_db.close()

    datums = (
        "water_temperature conductivity salinity water_level hourly_height "
        "high_low daily_mean monthly_mean one_minute_water_level predictions "
        "air_gap currents currents_predictions ofs_water_level"
    ).split()
    recordables = {"water_temperature", "conductivity", "salinity", "water_level"}
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

    ocean_reports = []
    failures = []

    for st in stations:
        rpt = {'src_id': st['id'], 'timestamp': timestamp}

        for datum in datums:
            if datum not in (st.get('datums') or []):
                if datum in recordables:
                    rpt[datum] = None
                continue

            data = request(st['id'], datum)
            if not isinstance(data, dict) and getattr(data, 'status_code', 0) >= 400:
                pprint(f"HTTP ERROR {data.status_code} for {datum} at {st['id']}")
                break
            if isinstance(data, dict) and data.get('error'):
                if datum in recordables:
                    rpt[datum] = None
                continue

            if datum == 'salinity':
                rpt[datum] = data['data'][0]['s']
            elif datum in recordables:
                rpt[datum] = data['data'][0]['v']

        pprint(f"### COOP Oceanography API: Queuing ocean report for {st['id']}")
        ocean_reports.append(rpt)
        sleep_fn(0.1)

    db = DBOperatorClass(table='oceanography')
    for rpt in ocean_reports:
        try:
            db.add(rpt.copy())
            db.commit()
        except Exception as e:
            pprint(f"DB Error inserting ocean report for {rpt['src_id']}: {e}")
            db.rollback()
            failures.append(rpt)
    db.close()

    return ocean_reports, failures


if __name__ == '__main__':
    run()
