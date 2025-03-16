import base64
from Crypto.Cipher import AES
from json import loads, dumps
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from DBOperator import DBOperator

app = FastAPI()

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Requests from frontend
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

@app.get("/vessels/", response_model=dict)
async def get_filtered_vessels(
    type: str = Query(None, description="Filter by vessel type"),
    origin: str = Query(None, description="Filter by country of origin"),
    status: str = Query(None, description="Filter by vessel status")
):
    """
    Fetch vessel data filter options.
    """
    db = connect_to_vessels()
    try:
        payload = {
            "Retrieved": datetime.now(),
            "Privileges": db.get_privileges(),
            "Table attribuets": db.get_attributes(),
            "filters": db.fetch_filter_options(),
            "payload": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    # Ignore empty filters
    filters = {key: value for key, value in {
        "type": type if type else None,
        "origin": origin if origin else None,
        "status": status if status else None
    }.items() if value}

    ### IF DB connection successful, attempt assembling payload
    print("### Fast Server: Assembling Payload...")
    try:
        # Return all vessels if no filters are provided
        payload["payload"] = db.query(filters) if filters else db.get_table()
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
