from pprint import pprint
from json import loads, dumps
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import connect, decrypt_password, filter_parser
from DBOperator import DBOperator
import linear_regression
import linear_regression_2

app = FastAPI()

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Requests from frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def welcome():
    '''
    Root handler
    '''
    return {"Message": "Hello :)",
            "Retrieved": datetime.now(),
           }

@app.get("/weather/")
async def weather():
    '''
    Weather query
    '''
    db = connect('meteorology')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            # Converting types to json throws an error now, so just providing
            # attributes themselves...
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for weather: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Should retrieve nothing rn
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        # raise HTTPException(status_code=501, detail=f"Coming soon")
        raise HTTPException(status_code=500, detail=f"Error fetching Weather data: {str(e)}")

@app.get("/ocean/")
async def ocean_data():
    '''
    Oceanography query
    '''
    db = connect('oceanography')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for ocean data: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Should retrieve nothing rn
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        # raise HTTPException(status_code=501, detail=f"Coming soon")
        raise HTTPException(status_code=500, detail=f"Error fetching ocean data: {str(e)}")

@app.get("/events/")
async def pull_events():
    '''
    Events/Alerts query
    '''
    db = connect('events')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        raise HTTPException(status_code=501, detail=f"Coming soon")
        # raise HTTPException(status_code=500, detail=f"Error fetching metadata for events: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Should retrieve nothing rn
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/users/")
async def users():
    '''
    Users query
    '''
    return {"Message": "Getting users!",
            "Retrieved": datetime.now(),
           }

@app.post("/addUser")
async def add_user(formData: dict):
    '''
    User registration handler
    '''
    print("### Websocket: Form data:")
    print(formData)
    return formData

@app.post("/login")
async def login(formData: dict):
    '''
    User login handler
    '''
    print(formData)
    # email = formData["email"]
    # decrypted_password = decrypt_password(formData["password"], secret_key="my-secret-key")
    return (formData)

@app.get("/stations/", response_model=dict)
async def get_stations():
    '''
    Stations query
    '''
    db = connect('sources')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        print(f"### Websocket: Error fetching metadata for stations:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for stations: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Currently only NOAA-COOP stations in table
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stations: {str(e)}")

@app.get("/vessels/", response_model=dict)
async def get_filtered_vessels(
    type: str = Query("", description="Filter by vessel type"),
    origin: str = Query(None, description="Filter by country of origin"),
    status: str = Query(None, description="Filter by vessel status")
):
    """
    Fetch filtered vessels.
    Fetch vessel data based on provided filters.
    """
    db = connect('vessels')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            "filters": db.fetch_filter_options(),
            "payload": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    # I'm confused here... we split types, but then we apply types in the
    # filters later to ignore emtpy filters?
    # Assemble filters
    types_list = type.split(',') if type else []
    filters = {}

    # Include filters only if they have values
    if types_list:
        filters["type"] = type.split(',') if type else []
    if origin:
        filters["flag"] = origin
    if status:
        filters["current_status"] = status.split(',') if status else []

    if not types_list:
        print("### Fast Server: All vessel types unchecked → Returning empty payload.")
        payload['payload'] = []
        payload["size"] = 0
        return payload

    print("### Fast Server: Assembling Payload...")
    # Ignore empty filters
    filters = {key: value for key, value in {
        "type": types_list,
        "flag": origin if origin else None,
        "current_status": status if status else None
    }.items() if value}

    # print(f"### Websocket: Filters:\n{filters}")

    if len(filters) > 0:
        queries = []
        filter_parser(filters,queries)
    # Proceed with query if filters are present, otherwise return all vessels
    print(f"### Websocket: Filters:\n{filters}")
    
    try:
        if filters:  # If any filters are provided
            queries = []
            filter_parser(filters, queries)

            # Remove duplicates from queries array
            queries = [dict(t) for t in {tuple(d.items()) for d in queries}]

        # print(f"### Websocket: query array:")
        # pprint(queries)
            print(f"### Websocket: query array:")
            pprint(queries)

            payload["payload"] = db.query(queries)
        else:
            # Return all vessels if no filters are provided
            payload["payload"] = db.get_table()

        payload["size"] = len(payload["payload"])
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vessels: {str(e)}")
    finally:
        db.close()

# FIXME: Weird bug where selecting a vessel and then selecting apply filters assumes zoning
@app.post("/zoning/", response_model=dict)
async def zone_vessels(data: dict):
    '''
    Zoning query. Collects Meteorological and oceanographic data, events,
    and vessels that are sourced from inside zone
    '''
    vessels = connect('vessels')
    met = connect('meteorology')
    oce = connect('oceanography')
    events = connect('events')
    sources = connect('sources')

    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": vessels.permissions,
            "attributes": [i for i in vessels.attrs.keys()],
            "payload": {}
        }
    except Exception as e:
        print(f"### Websocket: Error fetching metadata for zoning:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    geom = data['geom']
    types = data['type'].split(',') if 'type' in data.keys() else []
    status = data['origin'].split(',') if 'origin' in data.keys() else []
    flags = data['flag'].split(',') if 'flag' in data.keys() else []

    pprint(geom)

    try:
        ### Getting Vessels
        payload['payload'].update({'vessels':[]})

        # NOTE: I HATE this implemenetation.
        for i in vessels.within(geom):
            if (i['type'] in types) or (i['flag'] in flags) or (i['current_status'] in status):
                payload['payload']['vessels'].append(i)

        payload['size'] = len(payload['payload'])

        # Pulling stations
        stations = [i['id'] for i in sources.within(geom)]
        payload['payload'].update({'stations': stations})

        ### Getting Meteorology
        # print("### Websocket: querying meteorology data matching station id:")
        # pprint(met.query([{'src_id': i} for i in stations]))
        payload['payload'].update({'weather': met.query([{'src_id': i} for i in stations])})

        ### Getting Oceanography
        payload['payload'].update({'oceanography': oce.query([{'src_id': i} for i in stations])})

        ### Getting events
        payload['payload'].update({'alerts': events.query([{'src_id': i} for i in stations])})

        return payload

    except Exception as e:
        print(f"### Websocket: Error fetching zoning data:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching zone data: {str(e)}")
    finally:
        vessels.close()

@app.get("/filters/", response_model=dict)
async def get_filter_options():
    db = connect('vessels')
    try:
        filter_options = db.fetch_filter_options()
        if not filter_options:
            raise HTTPException(status_code=404, detail="No filter options found.")
        return filter_options
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filter options: {str(e)}")
    finally:
        db.close()

@app.post("/vessels/add/")
async def add_vessel(data: dict):
    db = connect('vessels')
    required_fields = ["id", "name", "type", "country_of_origin", "status", "latitude", "longitude"]

    if not all(field in data for field in required_fields):
        raise HTTPException(status_code=400, detail=f"Missing required fields. Required fields are: {required_fields}")

    try:
        db.add(data)
        db.commit()
        return {"status": "success", "message": "Vessel added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding vessel: {str(e)}")
    finally:
        db.close()

@app.get("/metadata/")
# WARNING: it brokie. Not important enough for me to figure out why imo
async def query_metadata():
    '''
    <query_description>
    '''
    ### Attempt DB connection
    db = connect('spatial_ref_sys')

    ### IF DB connection successful, attempt assembling payload
    print("### Server: Assembling Payload...")
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": db.query([{'srid',4326}]) # Spatial reference system, Global scope (https://spatialreference.org/ref/epsg/4326/)
                   }
        print("### Server: Payload assembled.")
    except Exception as e:
        print(f"### Server: Error retrieving metadata:\n{e}")
        print("### Fast Server: Error assembling payload.")
        payload = JSONResponse(
            status_code=500,
            content={"Error": "Error assembling payload."}
        )
    finally:
        db.close() # Closes table instance
        return payload
















    
@app.get("/prediction/{lon}/{lat}")
async def predict_path(lon: float, lat: float):
    print(f"Received coordinates - Longitude: {lon}, Latitude: {lat}")
    # linear_regression.perform_training_manually()
    predictions = linear_regression_2.perform_vessel_prediction(lat, lon)
    return predictions.to_dict(orient="records")
