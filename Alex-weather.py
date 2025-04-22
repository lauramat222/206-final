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
            current = next((p for p in forecast['properties']['periods'] if p['isDaytime']), None)

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
        time.sleep(1)
    return pd.DataFrame(results)

def save_results(df, output_file='city_weather_analysis.csv'):
    #save results to csv in SI 206/SI-final folder
    base_path = os.path.expanduser('~')
    output_path = os.path.join(base_path, 'Desktop', 'SI 206 Folder', 'SI-final', output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path

def insert_state_and_get_id(cur, state_code):
    cur.execute("INSERT OR IGNORE INTO states (code) VALUES (?)", (state_code,))
    cur.execute("SELECT id FROM states WHERE code = ?", (state_code,))
    return cur.fetchone()[0]

def insert_condition_and_get_id(cur, condition_desc):
    cur.execute("INSERT OR IGNORE INTO conditions (description) VALUES (?)", (condition_desc,))
    cur.execute("SELECT id FROM conditions WHERE description = ?", (condition_desc,))
    return cur.fetchone()[0]

def save_to_database(df, db_path='updated_events_weather.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for _, row in df.iterrows():
        city = row['city']
        state = row['state']
        latitude = row['latitude']
        longitude = row['longitude']
        temp = row['current_temp']
        condition = row['conditions']
        humidity = row['humidity']
        updated = row['updated']

        state_id = insert_state_and_get_id(cur, state)
        condition_id = insert_condition_and_get_id(cur, condition)

        cur.execute("""
            INSERT OR IGNORE INTO cities (city, state_id, latitude, longitude)
            VALUES (?, ?, ?, ?)
        """, (city, state_id, latitude, longitude))

        cur.execute("""
            INSERT INTO weather_data (city, state_id, current_temp, condition_id, humidity, updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (city, state_id, temp, condition_id, humidity, updated))

    conn.commit()
    conn.close()

def initialize_database(db_path='updated_events_weather.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT UNIQUE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city TEXT,
            state_id INTEGER,
            latitude REAL,
            longitude REAL,
            PRIMARY KEY (city, state_id),
            FOREIGN KEY (state_id) REFERENCES states(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            city TEXT,
            state_id INTEGER,
            current_temp REAL,
            condition_id INTEGER,
            humidity REAL,
            updated TEXT,
            FOREIGN KEY (city, state_id) REFERENCES cities(city, state_id),
            FOREIGN KEY (condition_id) REFERENCES conditions(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            state_id INTEGER,
            capacity INTEGER,
            url TEXT,
            FOREIGN KEY (city, state_id) REFERENCES cities(city, state_id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
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
    initialize_database()
    cities = load_city_data()
    if cities is not None and all(col in cities.columns for col in ['city', 'state', 'latitude', 'longitude']):
        weather_df = analyze_cities_weather(cities)
        if not weather_df.empty:
            save_results(weather_df)
            save_to_database(weather_df)
            print_results(weather_df)

if __name__ == "__main__":
    main()