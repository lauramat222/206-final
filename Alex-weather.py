
import requests
import pandas as pd
import time
import json


HEADERS = {
    'User-Agent': 'SI_final_project/1.0 (aywarner@umich.edu)',
    'Accept': 'application/geo+json'
}

def load_city_data(file_path='top_100_us_cities_lat_lon.csv'):
    #Load city data from Dara's file
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {len(df)} cities from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading city data: {e}")
        return None

def get_weather_data(latitude, longitude):
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
        print(f"Error fetching weather for {latitude},{longitude}: {str(e)}")
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
    #save results to csv in SI 206/SI-final folder

    base_path = os.path.expanduser('~')  # Gets your home directory
    output_path = os.path.join(base_path, 'Desktop', 'SI 206 Folder', 'SI-final', output_file)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    return output_path

def print_results(df):
    print("\nWEATHER RESULTS")
    print("="*50)
    for _, row in df.iterrows():
        print(f"\n{row['city']}, {row['state']}:")
        print(f"  Current Temp: {row['current_temp']}°{row['temp_unit']}")
        print(f"  Conditions: {row['conditions']}")
        print(f"  Humidity: {row['humidity']}%")
        print(f"  Forecast Office: {row['forecast_office']}")
        print(f"  Last Updated: {row['updated']}")
    print("\n" + "="*50)

def main():
    print("Starting weather data collection...")

    #load city data
    cities = load_city_data

    if cities is not None:
        required_cols = ['city', 'state', 'latitude', 'longitude']
        if all(col in cities.columns for col in required_cols):
        # Analyze weather data
            weather_df = analyze_cities_weather(cities)
            
            if not weather_df.empty:
                # Save results
                output_path = save_results(weather_df)
                print(f"\nSaved results to: {output_path}")
                 
                # Print results
                print_results(weather_df)
                    
                # Show sample data
                print("\nSAMPLE DATA (first 5 rows):")
                print(weather_df.head())
            else:
                print("No weather data was retrieved. Check API errors above.")
        else:
            print("Error: Input file missing required columns (city, state, latitude, longitude)")

if __name__ == "__main__":
    main()