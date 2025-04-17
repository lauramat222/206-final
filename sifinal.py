import sqlite3
import requests
import time
from typing import List, Dict, Any

API_KEY = "t0OyBfrw3dS1yZjgLYIGCWrh68Pkb7bN"  # Replace with your actual key
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events/"
DB_PATH = "events_weather.db"

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(DB_PATH)

def fetch_events(city: str, state: str) -> List[Dict[str, Any]]:
    """Fetch events from Ticketmaster API"""
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
    """Store events and venues in the database if data is complete"""
    conn = get_db_connection()
    cur = conn.cursor()

    for event in events:
        try:
            # Ensure venue info is available
            if '_embedded' not in event or 'venues' not in event['_embedded']:
                print(f"Skipping event {event.get('id')} — no venue info")
                continue

            venue = event['_embedded']['venues'][0]

            # Skip events with missing price info
            if 'priceRanges' not in event or not event['priceRanges']:
                print(f"Skipping event {event.get('id')} — no price info")
                continue

            price_range = event['priceRanges'][0]
            price_min = price_range.get('min')
            price_max = price_range.get('max')

            if price_min is None or price_max is None:
                print(f"Skipping event {event.get('id')} — price min/max missing")
                continue

            # Skip events missing dates
            local_date = event.get('dates', {}).get('start', {}).get('localDate')
            local_time = event.get('dates', {}).get('start', {}).get('localTime')
            if not local_date:
                print(f"Skipping event {event.get('id')} — no date")
                continue

            # Insert venue
            cur.execute("""
                INSERT OR IGNORE INTO venues VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venue.get('id'),
                venue.get('name'),
                venue.get('city', {}).get('name'),
                venue.get('state', {}).get('stateCode'),
                venue.get('capacity'),
                venue.get('url')
            ))

            # Insert event
            cur.execute("""
                INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    cities = conn.execute("SELECT city, state FROM cities").fetchall()
    conn.close()
    
    for city, state in cities:
        print(f"Processing {city}, {state}...")
        events = fetch_events(city, state)
        if events:
            store_events(events)
        time.sleep(1)  # Respect API rate limits

if __name__ == "__main__":
    main()
    




