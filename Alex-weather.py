import requests
import pandas as pd
import time
import os
import sqlite3


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

def get_weather_data(latitude, longitude, retries=3):
    """get weather from weather.gov API with retries"""
    for attempt in range(retries):
        try:
            points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
            response = requests.get(points_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            grid_data = response.json()['properties']
            
            forecast_url = grid_data['forecast']
            forecast = requests.get(forecast_url, headers=HEADERS, timeout=30).json()
            
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
            print(f"Attempt {attempt + 1} failed for {latitude},{longitude}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
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

def initialize_database(db_path='events_weather.db'):
    """Create all tables needed for the project"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='old_cities'")
    if cur.fetchone():
        cur.execute("DROP TABLE old_cities")

    for table in ['cities', 'weather_data', 'venues', 'events']:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cur.fetchone():
            cur.execute(f"ALTER TABLE {table} RENAME TO old_{table}")
    
    # Create new tables
    cur.executescript("""
        CREATE TABLE cities (
            city TEXT,
            state TEXT,
            latitude REAL,
            longitude REAL,
            PRIMARY KEY (city, state)
        );
        
        CREATE TABLE weather_data (
            city TEXT,
            state TEXT,
            current_temp REAL,
            conditions TEXT,
            humidity REAL,
            updated TEXT,
            FOREIGN KEY (city, state) REFERENCES cities(city, state)
        );
        
        CREATE TABLE venues (
            id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            state TEXT,
            capacity INTEGER,
            url TEXT,
            FOREIGN KEY (city, state) REFERENCES cities(city, state)
        );
        
        CREATE TABLE events (
            id TEXT PRIMARY KEY,
            name TEXT,
            venue_id TEXT,
            date TEXT,
            time TEXT,
            price_min REAL,
            price_max REAL,
            ticket_status TEXT,
            url TEXT,
            FOREIGN KEY (venue_id) REFERENCES venues(id)
        );
    """)
    conn.commit()
    conn.close()


def save_to_database(df, db_path='events_weather.db'):
    """Save weather data to SQLite database"""
    conn = sqlite3.connect(db_path)
    
    # Save cities and weather data
    df[['city', 'state', 'latitude', 'longitude']].to_sql(
        'cities', conn, if_exists='replace', index=False)
        
    df[['city', 'state', 'current_temp', 'conditions', 'humidity', 'updated']].to_sql(
        'weather_data', conn, if_exists='replace', index=False)
    
    conn.close()


def main():
    print("Starting weather data collection...")
    
    initialize_database()

    # load city data
    cities = load_city_data()

    if cities is not None:
        required_cols = ['city', 'state', 'latitude', 'longitude']
        if all(col in cities.columns for col in required_cols):
            # Analyze weather data
            weather_df = analyze_cities_weather(cities)
            
            if not weather_df.empty:
                output_path = save_results(weather_df)
                save_to_database(weather_df)
                try:
                    import visualizations
                    visualizations.plot_weather_vs_events()
                except ImportError:
                    print("Visualizations module not available")


if __name__ == "__main__":
    main()