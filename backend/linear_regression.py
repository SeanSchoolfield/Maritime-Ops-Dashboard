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

def train_and_save_model(data, model_filename):
    data['BaseDateTime'] = pd.to_datetime(data['BaseDateTime'])
    data = data.sort_values(by='BaseDateTime')
    data['TimeElapsed'] = (data['BaseDateTime'] - data['BaseDateTime'].min()).dt.total_seconds() / 3600.0
    data['Distance'] = data.apply(lambda row: calculate_distance(row, data), axis=1)
    data['Total Distance'] = data['Distance'].cumsum()

    time_passed = data['TimeElapsed'].values.reshape(-1, 1)
    lat = data['LAT'].values
    lon = data['LON'].values
    lat_model = LinearRegression().fit(time_passed, lat)
    lon_model = LinearRegression().fit(time_passed, lon)

    joblib.dump(lat_model, f'{model_filename}_lat_model.pkl')
    joblib.dump(lon_model, f'{model_filename}_lon_model.pkl')

    print(f"Models saved as {model_filename}_lat_model.pkl and {model_filename}_lon_model.pkl")

def perform_training_manually():
    data = pd.read_json('filtered_data.json')
    model_filename = 'vessel_model'
    train_and_save_model(data, model_filename)

if __name__ == '__main__':
    data = pd.read_json('filtered_data.json')
    model_filename = 'vessel_model'
    train_and_save_model(data, model_filename)