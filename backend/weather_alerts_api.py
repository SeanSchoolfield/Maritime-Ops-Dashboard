import requests
from pprint import pprint
from json import loads, dumps

alerts_url = "https://api.weather.gov/alerts?zone=IAC129"
alerts = requests.get(alerts_url)
print(f"STATUS: {alerts.status_code}")

payload = alerts.json()['features']
pagination_url = alerts.json()['pagination']['next']

print(f"Pagination URI: {pagination_url}") if pagination_url else print()

print(f"Number of alerts retrieved: {len(payload)}\n")

print("Data:")
print()

# TODO: Format and import into events
"""
id = Alert ID (??)
src_id ??? <- Reprots Source name, but I'd prefer source CWA
timestamp = sent time
effective = Effective time
end_time = End time
active = '{if effective <= current_time < end_time}'
type = '{Category}-{messageType}'
description = Description
expires = Alert Expiration time
instructions = Instructions
urgency = Urgency
severity = Severity
headline = Headline
"""

for alert in payload:
    # Do I want to use this, or auto generate an ID?
    pprint(alert)
    input()
    
    print("##########\nAlert ID:")
    pprint(alert['id'].split(':')[-1])
    print('##########\n')

    print("Sender:") # Source ID
    pprint(alert['properties']['senderName'])
    pprint(alert['properties']['parameters']['AWIPSidentifier'])
    print()

    print("sent time:") # timestamp
    pprint(alert['properties']['sent'])

    print("Effective time:") # begin
    pprint(alert['properties']['effective'])

    print("End time:") # end
    pprint(alert['properties']['ends'])


    print("Alert Expiration time:") # Might be good to store to use for updates on events
    pprint(alert['properties']['expires'])

    print("Onset time:")
    pprint(alert['properties']['onset'])

    print()

    print("Replacement time:")
    pprint(alert['properties']['replacedAt']) if 'replacedAt' in alert['properties'].keys() else print("Nothing to replace")

    print("Replaced by URI:") # ID to check upon expiration, if exists. Otherwise, just broadly query
    if 'replacedBy' in alert['properties'].keys():
        pprint(alert['properties']['replacedBy'])
        print("AlertID replacing this one:")
        pprint(alert['properties']['replacedBy'].split(':')[-1])
    else:
        print("Nothing to replace")
    print()

    # NOTE: Should I save this? GFW Vessel Events also apparently reports some "region"
    print("Affected Zones:") # Should I store an array of impacted Zones, or should I have zones store active alerts for their region?
    pprint(alert['properties']['geocode']['UGC'])
    pprint(alert['properties']['areaDesc'])
    print()

    # should I just store all of this in events.description?
    print("Category:") # type? Or just type=MET
    pprint(alert['properties']['category'])
    print()

    print("Severity:")
    pprint(alert['properties']['severity'])
    print()

    print("Urgency:")
    pprint(alert['properties']['urgency'])
    print()

    print("Certainty:")
    pprint(alert['properties']['certainty'])
    print()

    print("Headline:")
    pprint(alert['properties']['parameters']['NWSheadline'][0])
    print()

    print("type:")
    pprint(alert['properties']['messageType'])
    print()

    print("Description:")
    pprint(alert['properties']['description'])
    print()

    print("Instructions:")
    pprint(alert['properties']['instruction'])
    print()

    print("Geometry:")
    pprint(alert['geometry'])
    print()

    input("### API Script: Continue?")





























