import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import joblib
from geopy.distance import geodesic

def calculate_distance(row, data):
    if row.name == 0:
        return 0
    prev_row = data.iloc[row.name - 1]
    return geodesic((prev_row['LAT'], prev_row['LON']), (row['LAT'], row['LON'])).km

def perform_prediction(vessel_data, lat_model, lon_model):
    vessel_data['BaseDateTime'] = pd.to_datetime(vessel_data['BaseDateTime'])
    vessel_data = vessel_data.sort_values(by='BaseDateTime')
    vessel_data['TimeElapsed'] = (vessel_data['BaseDateTime'] - vessel_data['BaseDateTime'].min()).dt.total_seconds() / 3600.0

    vessel_data['Distance'] = vessel_data.apply(lambda row: calculate_distance(row, vessel_data), axis=1)
    vessel_data['Total Distance'] = vessel_data['Distance'].cumsum()
    future_times = np.array([vessel_data['TimeElapsed'].max() + i for i in range(1, 25)]).reshape(-1, 1)
    predicted_lats = lat_model.predict(future_times)
    predicted_lons = lon_model.predict(future_times)
    predictions = pd.DataFrame({'Hours Ahead': range(1, 25),
                                'Predicted LAT': predicted_lats,
                                'Predicted LON': predicted_lons})

    # print(f"Predictions for Vessel ID {vessel_data['MMSI'].iloc[0]}:\n")
    
    # print(predictions)
    # print()
    # print(f"Starting position: Latitude = {vessel_data['LAT'].iloc[0]}, Longitude = {vessel_data['LON'].iloc[0]}")
    # print(f"Last known position of the vessel: Latitude = {vessel_data['LAT'].iloc[-1]}, Longitude = {vessel_data['LON'].iloc[-1]}")

def load_models():
    lat_model = joblib.load('vessel_model_lat_model.pkl')
    lon_model = joblib.load('vessel_model_lon_model.pkl')
    return lat_model, lon_model

def predict_vessel_path(start_lat, start_lon, lat_model, lon_model, hours_ahead=72):
    time_periods = np.array([i for i in range(1, hours_ahead + 1)]).reshape(-1, 1)
    delta_lats = lat_model.predict(time_periods) - lat_model.predict([[0]])  # Delta from initial
    delta_lons = lon_model.predict(time_periods) - lon_model.predict([[0]])  # Delta from initial
    predicted_lats = start_lat + delta_lats
    predicted_lons = start_lon + delta_lons
    predictions = pd.DataFrame({
        'Hours Ahead': range(1, hours_ahead + 1),
        'Predicted LAT': predicted_lats,
        'Predicted LON': predicted_lons
    })

    # print(f"Predictions for new vessel starting at Latitude {start_lat}, Longitude {start_lon}:")
    # print(predictions)

    return predictions


def perform_vessel_prediction(start_lat, start_lon):
    lat_model, lon_model = load_models()
    predictions = predict_vessel_path(start_lat, start_lon, lat_model, lon_model)
    return predictions


if __name__ == '__main__':
    data = pd.read_json('filtered_data.json')
    lat_model = joblib.load('vessel_model_lat_model.pkl')
    lon_model = joblib.load('vessel_model_lon_model.pkl')

    selected_vessel_id = "367067950"
    vessel_data = data[data['MMSI'].astype(str) == str(selected_vessel_id)]
    if vessel_data.empty:
        print(f"No data found for vessel with ID {selected_vessel_id}")
    else:
        perform_prediction(vessel_data, lat_model, lon_model)