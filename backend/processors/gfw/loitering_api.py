import os
import sys
import requests
from pprint import pprint
from json import dumps
from ...DBOperator import DBOperator
from datetime import datetime
import pytz
from kafka import KafkaProducer

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8'),
    )

def process_loitering_events(producer=None):
    if producer is None:
        producer = get_kafka_producer()

    token = os.environ.get("TOKEN")
    if not token:
        sys.exit("No GFW API Token provided.")

    vessels_operator = DBOperator(table='vessels')
    events_operator = DBOperator(table='events')

    now = datetime.now()
    utc = pytz.UTC

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "datasets": ["public-global-loitering-events:latest"],
        "startDate": "2024-01-01",
        "endDate": now.strftime("%Y-%m-%d"),
    }

    events_url = "https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
    response = requests.post(events_url, headers=headers, json=data)
    print("Status Code:", response.status_code)

    if response.status_code not in [200, 201]:
        print("Response content:")
        print(response.text)
        sys.exit("Failed to fetch events.")

    events_data = response.json().get("entries", [])

    for event in events_data:
        try:
            event_type = event['type']
            vessel = event.get("vessel", {})
            vessel_name = vessel.get("name", "Unknown")
            mmsi = vessel.get("mmsi") or vessel.get("ssvid", "Unknown")

            start = datetime.fromisoformat(event['start'])
            end = datetime.fromisoformat(event['end'])
            timestamp = event['end'] if utc.localize(now) > end else event['start']

            speed = event[event_type].get('averageSpeedKnots', 0)
            status = 'LOITERING' if speed == 0 else 'LIMITED MOVEMENT'

            lat = event['position']['lat']
            lon = event['position']['lon']
            dist_from_port = event['distances'].get('endDistanceFromPortKm')
            dist_from_shore = event['distances'].get('endDistanceFromShoreKm')

            entity = {
                "id": event['id'],
                "src_id": mmsi,
                "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
                "effective": event['start'],
                "end_time": event['end'],
                "active": start <= utc.localize(now) < end,
                "type": event_type.upper(),
                "description": f"{vessel_name} ({mmsi}) has been reported loitering",
                "expires": event['end'],
                "instructions": "None",
                "urgency": "low",
                "severity": "low",
                "headline": f"{vessel_name} found loitering"
            }

            producer.send("GFW", key=mmsi, value=entity)
            print(f"Kafka: Sent event for vessel {mmsi}")

        except Exception as e:
            print(f"Error processing event {event.get('id')}: {e}")

    producer.flush()

if __name__ == "__main__":
    process_loitering_events()
