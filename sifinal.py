import sqlite3
import requests
from typing import Optional, Dict, Any, List 

apikey = "t0OyBfrw3dS1yZjgLYIGCWrh68Pkb7bN"
baseurl = "https://app.ticketmaster.com/discovery/v2/events/"

def fetch_events_by_city(city: str, state: str) -> Optional[List[Dict[str, Any]]]:
    params = {
        'apikey': apikey,
        'city': city,
        'stateCode': state,
        'countryCode': 'US',
        'size': 5  # Limit for testing
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if '_embedded' in data and 'events' in data['_embedded']:
            return data['_embedded']['events']
        else:
            print(f"No events found for {city}, {state}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {city}, {state}: {e}")
        return []
    
    def load_city_data(csv_filename: str) -> List[Dict[str, str]]:
        with open(csv_filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    
    def store_events(db_name: str, events: List[Dict[str, Any]]):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                name TEXT,
                city TEXT,
                state TEXT,
                date TEXT,
                locale TEXT
            )
        """)

    for event in events:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO events (id, name, city, state, date, locale)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event['id'],
                event['name'],
                event['_embedded']['venues'][0]['city']['name'],
                event['_embedded']['venues'][0]['state']['stateCode'],
                event['dates']['start']['localDate'],
                event.get('locale', '*')
            ))
        except Exception as e:
            print(f"Failed to insert event: {e}")

    conn.commit()
    conn.close()

    if __name__ == "__main__":
        cities = load_city_data("top_100_us_cities_lat_lon.csv")
    
        for city_entry in cities[:10]:  # Only do top 10 cities to start
            city = city_entry["city"]
            state = city_entry["state"]
            print(f"Fetching events for {city}, {state}")
        
            events = fetch_events_by_city(city, state)
            if events:
                store_events("ticketmaster_events.db", events)
    
    




