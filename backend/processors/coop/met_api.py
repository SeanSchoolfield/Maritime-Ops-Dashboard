import csv
import requests
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep
from ...DBOperator import DBOperator

"""
// Thinkin' Thoughts
- I wonder if it's worth it to combine this and the NWS Forecast API into one
  that pulls stations based on Within() Zone, so Missing data can be
  potentially accounted between one another

// TODO
- Convert types to coincide with DB
- Test
    - improve logging
    - error handling
    - Adding/modifying DB entries
"""


def request(id: str, product: str):
    """
    Fetch a single datum from the NOAA CO-OP API. Returns JSON on success,
    or a Response object on HTTP error.
    """
    url = (
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
        f"?date=latest&station={id}&product={product}"
        f"&datum=STND&time_zone=gmt&units=english&format=json"
    )
    resp = requests.get(url)
    if resp.status_code >= 400:
        return resp
    return resp.json()


def main():
    weather_reports = []
    notices = []

    source_op = DBOperator(table='sources')
    stations = source_op.query([{'type': 'NOAA-COOP'}])
    source_op.close()

    things = ['air_temperature', 'wind', 'visibility', 'humidity']
    timestamp = datetime.now()

    for station in stations:
        station_id = station['id']
        station_name = station.get('name', station_id)

        report = {
            'src_id': station_id,
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        }

        for thing in things:
            if thing not in station.get('datums', []):
                pprint(f"No {thing} data for station {station_name} ({station_id})")
                if thing == 'wind':
                    report.update({'wind_heading': None, 'wind_speed': None})
                else:
                    report[thing] = None
                continue

            data = request(station_id, thing)
            if hasattr(data, 'status_code') and data.status_code >= 400:
                pprint(f"HTTP ERROR {data.status_code} for {thing} at station {station_id}")
                break
            if isinstance(data, dict) and data.get('error'):
                pprint(f"{thing} no longer recorded at station {station_name} ({station_id})")
                if thing == 'wind':
                    report.update({'wind_heading': None, 'wind_speed': None})
                else:
                    report[thing] = None
                continue

            entry = data['data'][0]
            if thing == 'wind':
                report['wind_heading'] = entry.get('d')
                report['wind_speed'] = entry.get('s')
            else:
                report[thing] = entry.get('v')

        report.update({
            'precipitation': None,
            'forecast': None,
            'event_id': None
        })
        pprint(f"### COOP Meteorology API: Queuing weather report for {station_id}")
        weather_reports.append(report)

        # Build notice report
        notice_resp = requests.get(
            f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}/notices.json"
        )
        if notice_resp.status_code in (200, 201):
            notice_data = notice_resp.json().get('notices', [])
            if notice_data:
                n = notice_data[0]
                notice = {
                    'src_id': station_id,
                    'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                    'effective': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end_time': (timestamp + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'active': True,
                    'type': 'Marine alert',
                    'description': n.get('text'),
                    'expires': (timestamp + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'instructions': 'None',
                    'urgency': 'low',
                    'severity': 'low',
                    'headline': n.get('name')
                }
                pprint(f"### COOP Meteorology API: Queuing notice for {station_id}")
                notices.append(notice)
        else:
            pprint(f"NOTICE HTTP ERROR {notice_resp.status_code} for station {station_id}")

        sleep(0.1)

    met_op = DBOperator(table='meteorology')
    for rpt in weather_reports:
        try:
            met_op.add(rpt)
            met_op.commit()
        except Exception as e:
            pprint(f"DB error saving weather report for {rpt['src_id']}: {e}")
            met_op.rollback()
    met_op.close()

    ev_op = DBOperator(table='events')
    for note in notices:
        try:
            ev_op.add(note)
            ev_op.commit()
        except Exception as e:
            pprint(f"DB error saving notice for {note['src_id']}: {e}")
            ev_op.rollback()
    ev_op.close()

    print(f"Done: {len(weather_reports)} weather reports, {len(notices)} notices processed.")


if __name__ == "__main__":
    main()
