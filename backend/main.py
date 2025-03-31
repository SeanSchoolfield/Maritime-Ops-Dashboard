import base64
from pprint import pprint
from Crypto.Cipher import AES
from json import loads, dumps
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

def connect_to_vessels() -> DBOperator:
    ### Attempt DB connection
    try:
        db = DBOperator(table='vessels')
        print("### Fast Server: Connected to vessels table")
        return db
    except Exception as e:
        print("### Fast Server: Unable connect to Vessels table")
        raise HTTPException(
            status_code=500,
            detail="Unable to connect to database."
        )

@app.get("/")
async def welcome():
    '''
    Example First Fast API Example
    '''
    return {"Message": "Welcome to FastAPI!",
            "Retrieved": datetime.now(),
           }

@app.get("/weather/")
async def weather():
    '''
    Weather query
    '''
    return {"Message": "Weather!",
            "Retrieved": datetime.now(),
           }

@app.get("/users/")
async def users():
    '''
    Users query
    '''
    return {"Message": "Getting users!",
            "Retrieved": datetime.now(),
           }

def decrypt_password(encrypted_password, secret_key):
    encrypted_data = base64.b64decode(encrypted_password)
    cipher = AES.new(secret_key.encode('utf-8'), AES.MODE_ECB)
    decrypted_bytes = cipher.decrypt(encrypted_data)
    return decrypted_bytes.strip().decode('utf-8')

@app.post("/addUser")
async def add_user(formData: dict):
    print(formData)
    return formData

@app.post("/login")
async def login(formData: dict):
    print(formData)
    # email = formData["email"]
    # decrypted_password = decrypt_password(formData["password"], secret_key="my-secret-key")
    return (formData)

def connect_to_vessels() -> DBOperator:
    ### Attempt DB connection
    try:
        db = DBOperator(table='vessels')
        print("### Fast Server: Connected to vessels table")
        return db
    except Exception as e:
        print("### Fast Server: Unable connect to Vessels table")
        raise HTTPException(
            status_code=500,
            detail="Unable to connect to database."
        )

def filter_parser(p: dict, result: list) -> None:
    """
    Quick lil recursion function to create a list of dictionaries that have one
    query-able value per attribute

    ### WARNING: Creates some duplicate queries when more than one attribute
    has more than 1 value. Pretty sure its cuz my recursive restraints suck so
    much ass. Shouldn't affect results since its a UNION query
    """
    x = {}
    for k, v in p.items():
        val = v if isinstance(v, list) else v.split(',')
        while len(val) > 1:
            q = p.copy()
            q[k] = val.pop(0)
            filter_parser(q,result)
        x.update({k: val[0]})
    result.append(x)

@app.get("/vessels/", response_model=dict)
async def get_filtered_vessels(
    type: str = Query("", description="Filter by vessel type"),
    origin: str = Query(None, description="Filter by country of origin"),
    status: str = Query(None, description="Filter by vessel status")
):
    """
    Fetch vessel data based on provided filters.
    """
    db = connect_to_vessels()
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attribuets": db.attrs,
            "filters": db.fetch_filter_options(),
            "payload": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    # Assemble filters
    types_list = type.split(',') if type else []
    filters = {}

    # Include filters only if they have values
    if types_list:
        filters["type"] = types_list

    if origin:
        filters["flag"] = origin

    if status:
        filters["current_status"] = status

    # Proceed with query if filters are present, otherwise return all vessels
    print(f"### Websocket: Filters:\n{filters}")
    
    try:
        if filters:  # If any filters are provided
            queries = []
            filter_parser(filters, queries)

            # Remove duplicates from queries array
            queries = [dict(t) for t in {tuple(d.items()) for d in queries}]

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

@app.get("/filters/", response_model=dict)
async def get_filter_options():
    db = connect_to_vessels()
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
    db = connect_to_vessels()
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
async def query_metadata():
    '''
    <query_description>
    '''
    ### Attempt DB connection
    try:
        operator = DBOperator(table='spatial_ref_sys')
    except:
        print("### Fast Server: Unable connect to spatial_ref_sys table")
        return JSONResponse(
            status_code=500,
            content={"Error": "Unable to establish database connection"}
        )

    ### IF DB connection successful, attempt assembling payload
    print("### Server: Assembling Payload...")
    try:
        payload = {"Message": "Metadata for Geometry",
                   "Retrieved": datetime.now(),
                   "Privileges": operator.get_privileges(),
                   "Total entities": operator.get_count(),
                   "Table attribuets": operator.get_attributes(),
                   "payload": operator.query(('srid',4326)) # Spatial reference system, Global scope (https://spatialreference.org/ref/epsg/4326/)
                   }
        print("### Server: Payload assembled.")
    except:
        print("### Fast Server: Error assembling payload.")
        payload = JSONResponse(
            status_code=400,
            content={"Error": "Error assembling payload."}
        )
    finally:
        operator.close() # Closes table instance
        return payload
    
@app.get("/prediction/{lon}/{lat}")
async def predict_path(lon: float, lat: float):
    print(f"Received coordinates - Longitude: {lon}, Latitude: {lat}")
    # linear_regression.perform_training_manually()
    predictions = linear_regression_2.perform_vessel_prediction(lat, lon)
    return predictions.to_dict(orient="records")
