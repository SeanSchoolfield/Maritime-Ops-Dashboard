import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps

"""
NOAA weather.gov API
- I can obtain the wfo and the zoneID through api.weather.gov/point/{}{}
    zoneID: [forecastZone] (and subsequent zone geometry)
    wfo: [cwa] [forecastOffice]

- Weather Forecast:
    1. Get point: https//api.weather.gov/point/{lat},{lon}
    2. Get forecast with response.properties.forecast

!!! NEEDS A POINT !!!
    - Could use existing lat/lon attrs from ships, COOP stations
    - OR could do some PostGIS calcs on zones to find central point and return forecast there?

    - "https://api.weather.gov/gridpoints/OAX/90,48/forecast/hourly"
        WFO code __________________________|  |   |
        lat __________________________________|   |
        lon ______________________________________|

    - REPORTS GEOMETRY!
    - How do I correlate wfo to coordinates???
        - pass vessel/point/port/station coordinates?

- Alerts:
    -"https://api.weather.gov/alerts?zone={zoneID}"
- Zone Geometry:
    - https://api.weather.gov/zones/forecast{zoneID}[Geometry]
"""

"""
Forecast sequence
"""
# my_location_url = "https://api.weather.gov/gridpoints/OAX/90,48/forecast/hourly"
# point_report = requests.get("https://api.weather.gov/points/41,-95.74")
# print(f"STATUS: {point_report.status_code}")
# pprint(point_report.json())

# forecast = requests.get(my_location_url)
# print(f"STATUS: {forecast.status_code}")
# pprint(forecast.json()['properties']['periods'][0])
