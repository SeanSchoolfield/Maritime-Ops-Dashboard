import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps

zones_url = "https://api.weather.gov/zones"
stations_url = "https://api.weather.gov/stations"
my_location_url = "https://api.weather.gov/gridpoints/OAX/90,48/forecast/hourly"
alerts_url = "https://api.weather.gov/alerts?zone=IAC129"

"""
NOAA weather.gov API
- Weather Forecast Office codes:
     AKQ, ALY, BGM, BOX, BTV, BUF, CAE, CAR, CHS, CLE, CTP, GSP, GYX, ILM, ILN, LWX, MHX, OKX, PBZ, PHI, RAH, RLX, RNK, ABQ, AMA, BMX, BRO, CRP, EPZ, EWX, FFC, FWD, HGX, HUN, JAN, JAX, KEY, LCH, LIX, LUB, LZK, MAF, MEG, MFL, MLB, MOB, MRX, OHX, OUN, SHV, SJT, SJU, TAE, TBW, TSA, ABR, APX, ARX, BIS, BOU, CYS, DDC, DLH, DMX, DTX, DVN, EAX, FGF, FSD, GID, GJT, GLD, GRB, GRR, ICT, ILX, IND, IWX, JKL, LBF, LMK, LOT, LSX, MKX, MPX, MQT, OAX, PAH, PUB, RIW, SGF, TOP, UNR, BOI, BYZ, EKA, FGZ, GGW, HNX, LKN, LOX, MFR, MSO, MTR, OTX, PDT, PIH, PQR, PSR, REV, SEW, SGX, SLC, STO, TFX, TWC, VEF, AER, AFC, AFG, AJK, ALU, GUM, HPA, HFO, PPG, STU, NH1, NH2, ONA, ONP

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
alert = requests.get(alerts_url)
print(f"STATUS: {alert.status_code}")
pprint(alert.json())

point_report = requests.get("https://api.weather.gov/points/41,-95.74")
print(f"STATUS: {point_report.status_code}")
pprint(point_report.json())

forecast = requests.get(my_location_url)
print(f"STATUS: {forecast.status_code}")
pprint(forecast.json()['properties']['periods'][0])
