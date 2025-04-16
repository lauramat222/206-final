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
    """Store events in the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    for event in events:
        try:
            venue = event['_embedded']['venues'][0]
            
            # Insert venue
            cur.execute("""
                INSERT OR IGNORE INTO venues VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venue['id'],
                venue.get('name'),
                venue.get('city', {}).get('name'),
                venue.get('state', {}).get('stateCode'),
                venue.get('capacity'),
                venue.get('url')
            ))
            
            # Insert event
            price_range = event.get('priceRanges', [{}])[0]
            cur.execute("""
                INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event['id'],
                event['name'],
                venue['id'],
                event['dates']['start'].get('localDate'),
                event['dates']['start'].get('localTime'),
                price_range.get('min'),
                price_range.get('max'),
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
    




