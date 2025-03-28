import requests
from pprint import pprint

for wfo in "AKQ, ALY, BGM, BOX, BTV, BUF, CAE, CAR, CHS, CLE, CTP, GSP, GYX, ILM, ILN, LWX, MHX, OKX, PBZ, PHI, RAH, RLX, RNK, ABQ, AMA, BMX, BRO, CRP, EPZ, EWX, FFC, FWD, HGX, HUN, JAN, JAX, KEY, LCH, LIX, LUB, LZK, MAF, MEG, MFL, MLB, MOB, MRX, OHX, OUN, SHV, SJT, SJU, TAE, TBW, TSA, ABR, APX, ARX, BIS, BOU, CYS, DDC, DLH, DMX, DTX, DVN, EAX, FGF, FSD, GID, GJT, GLD, GRB, GRR, ICT, ILX, IND, IWX, JKL, LBF, LMK, LOT, LSX, MKX, MPX, MQT, OAX, PAH, PUB, RIW, SGF, TOP, UNR, BOI, BYZ, EKA, FGZ, GGW, HNX, LKN, LOX, MFR, MSO, MTR, OTX, PDT, PIH, PQR, PSR, REV, SEW, SGX, SLC, STO, TFX, TWC, VEF, AER, AFC, AFG, AJK, ALU, GUM, HPA, HFO, PPG, STU, NH1, NH2, ONA, ONP".split(', '):
    wfo = 'OAX'### DEBUG
    station_url = f"https://api.weather.gov/offices/{wfo}"
    station = requests.get(station_url)
    print(f"STATUS: {station.status_code}")
    pprint(station.json())

    # TODO: Format and port into DB

    address = station.json()['address']
    tele = station.json()['telephone']
    observation_stations = station.json()['approvedObservationStations']
    station_id = station.json()['id']
    station_name = station.json()['name']
    forecast_zones = [i.split('/')[-1] for i in station.json()['responsibleForecastZones']]
    # responsible_zones = station.json()['responsibleCounties']

    """

    """

    print(f"Station ID: {station_id}")
    print(f"Station Name: {station_name}")
    print(f"Region: USA-{address['addressRegion']}")
    print("Timezone: ???") # TODO: Dunno how to retrieve
    print("Type: NOAA-MET")
    print("Geometry: ???") # TODO: How to retrieve?
    print(f"Datums: {['Events', 'Meteorology']}")
    # Do I save ???
    print("Responsible forecast zones:") # datums ???
    pprint(forecast_zones)

    # Do I save the following?
    # print("Address:")
    # pprint(address)
    # print(f"Phone: {tele}")
    # fire_zones = station.json()['responsibleFireZones']
    # print("Responsible Fire zones:")
    # pprint(fire_zones)
    # print("Approved subsidiary stations:")
    # pprint(observation_stations)

    input("### API Script: Continue?")
























