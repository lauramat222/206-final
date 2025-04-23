import sqlite3
import requests
import time
from typing import List, Dict, Any

API_KEY = "t0OyBfrw3dS1yZjgLYIGCWrh68Pkb7bN"  # consumer key
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events/"
DB_PATH = "updated_events_weather.db"

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(DB_PATH)

def insert_state_and_get_id(cur, state_code):
    cur.execute("INSERT OR IGNORE INTO states (code) VALUES (?)", (state_code,))
    cur.execute("SELECT id FROM states WHERE code = ?", (state_code,))
    return cur.fetchone()[0]

def fetch_events(city: str, state: str) -> List[Dict[str, Any]]:
    params = {
        'apikey': API_KEY,
        'city': city,
        'stateCode': state,
        'countryCode': 'US',
        'size': 20,
        'sort': 'date,asc'
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('_embedded', {}).get('events', [])
    except Exception as e:
        print(f"Error fetching events for {city}, {state}: {str(e)}")
        return []

def store_events(events: List[Dict[str, Any]]):
    conn = get_db_connection()
    cur = conn.cursor()

    for event in events:
        try:
            if '_embedded' not in event or 'venues' not in event['_embedded']:
                continue

            venue = event['_embedded']['venues'][0]

            if 'priceRanges' not in event or not event['priceRanges']:
                continue

            price_range = event['priceRanges'][0]
            price_min = price_range.get('min')
            price_max = price_range.get('max')

            if price_min is None or price_max is None:
                continue

            local_date = event.get('dates', {}).get('start', {}).get('localDate')
            local_time = event.get('dates', {}).get('start', {}).get('localTime')
            if not local_date:
                continue

            venue_city = venue.get('city', {}).get('name')
            venue_state = venue.get('state', {}).get('stateCode')
            state_id = insert_state_and_get_id(cur, venue_state)

            cur.execute("""
                INSERT OR IGNORE INTO cities (city, state_id, latitude, longitude)
                VALUES (?, ?, NULL, NULL)
            """, (venue_city, state_id))

            cur.execute("""
                INSERT OR IGNORE INTO venues (id, name, city, state_id, capacity, url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venue.get('id'),
                venue.get('name'),
                venue_city,
                state_id,
                venue.get('capacity'),
                venue.get('url')
            ))

            cur.execute("""
                INSERT OR IGNORE INTO events (id, name, venue_id, date, time, price_min, price_max, ticket_status, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get('id'),
                event.get('name'),
                venue.get('id'),
                local_date,
                local_time,
                price_min,
                price_max,
                event.get('dates', {}).get('status', {}).get('code'),
                event.get('url')
            ))

        except Exception as e:
            print(f"Error storing event {event.get('id')}: {str(e)}")

    conn.commit()
    conn.close()

def main():
    conn = get_db_connection()
    cities = conn.execute("SELECT city, code FROM cities JOIN states ON cities.state_id = states.id").fetchall()
    conn.close()

    for city, state_code in cities:
        print(f"Processing {city}, {state_code}...")
        events = fetch_events(city, state_code)
        if events:
            store_events(events[:25])
        time.sleep(1)

if __name__ == "__main__":
    main()
    




