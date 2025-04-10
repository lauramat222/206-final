
import requests
import pandas as pandas
import time
import json


HEADERS = {
    'User-Agent': 'SI_final_project/1.0 (aywarner@umich.edu)',
    'Accept': 'application/geo+json'
}

def load_city_data(file_path):
    #Load city data from Dara's file
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        print(f"Error loading city data: {e}")
        return None

def def_weather_data(lat, lon):
    #get weather from weather.gov API"
    try:
        # getting grid endpoint"
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        response = requests.get(points_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        grid_data = response.json()['properties']

        #get forcase of cities
        

        




#api_key = "c3adecaa2b5b7f29047c3710b51c5952"
#base_url = "http://api.weatherstack.com/historical"

#for day in range(1,32):
    #date = f'2024-{day}-01'
    #params = {
        #'access_key': api_key,
        #'query': 'New York',
        #'historical_date': date
    #}

    #response = requests.get(base_url, params=params)
    #data = response.json()

    #print(data)

    #if response.status_code == 200:
       # print("Current weather in New York City:")
        #print(f"Temperature: {data['current']['temperature']}°C")
        #print(f"Weather description: {data['current']['weather_descriptions'][0]}")
       # print(f"Humidity: {data['current']['humidity']}%")
       # print(f"Wind speed: {data['current']['wind_speed']} km/h")
       # print(f"Observation time: {data['current']['observation_time']}")
    #else:
        #print(f"Error: {data.get('error', {}).get('info', 'Unknown error')}")