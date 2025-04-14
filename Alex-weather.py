
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
        forecast_url = grid_data['forecast']
        forecast = requests.get(forecast_url, headers=HEADERS, timeout=10).json()

        # get current conditions
        current = next(
            (p for p in forecast['properties']['periods'] if p['isDaytime']),
            None
        )
        
        return {
            'forecast_office': grid_data.get('forecastOffice'),
            'grid_id': f"{grid_data['gridId']}/{grid_data['gridX']},{grid_data['gridY']}",
            'current_temp': current['temperature'],
            'temp_unit': current['temperatureUnit'],
            'conditions': current['shortForecast'],
            'humidity': current.get('relativeHumidity', {}).get('value'),
            'updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error fetching weather for {lat},{lon}: {str(e)}")
        return None

def analyze_cities_weather(city_data):
    # process the cities and compile all weather data
    results = []
    for _, row in city_data.iterrows():
        print(f"Processing {row['city']}, {row['state']}...")

        weather = get_weather_data(row['latitude'], row['longitude'])

        if weather:
            record = {
                'city': row['city'],
                'state': row['state'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                **weather
            }
            results.append(record)
        
        time.sleep(1)  # Respect rate limits
    
    return pd.DataFrame(results)

def save_results(df, output_file='city_weather_analysis.csv'):
    #save results
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

    #execution
    if __name__ == "__main__":
    # Load Dara's data
        cities = load_city_data('Dara-soup.py.csv')
    
        if cities is not None:
            # Verify required columns exist
            required_cols = ['city', 'state', 'latitude', 'longitude']
            if all(col in cities.columns for col in required_cols):
                # Analyze weather data
                weather_df = analyze_cities_weather(cities)
                
                # Save and show results
                save_results(weather_df)
                print("\nSample results:")
                print(weather_df.head())
            else:
                print("Error: Input file missing required columns (city, state, latitude, longitude)")