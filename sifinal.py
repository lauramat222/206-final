import sqlite3
import requests
from typing import Optional, Dict, Any, List
import time

API_KEY = "t0OyBfrw3dS1yZjgLYIGCWrh68Pkb7bN"  # Replace with your actual key
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events/"

def fetch_events(city: str, state: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch events from Ticketmaster API for a specific city"""
    params = {
        'apikey': API_KEY,
        'city': city,
        'stateCode': state,
        'countryCode': 'US',
        'size': 20,  # Max allowed per request
        'sort': 'date,asc'
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('_embedded', {}).get('events'):
            print(f"No events found for {city}, {state}")
            return None
            
        return data['_embedded']['events']
    except Exception as e:
        print(f"Error fetching events for {city}, {state}: {str(e)}")
        return None

def store_events(db_path: str, events: List[Dict[str, Any]]):
    """Store events in the existing database"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create tables if they don't exist
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS venues (
            id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            state TEXT,
            capacity INTEGER,
            url TEXT
        );
        
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
        
        CREATE TABLE IF NOT EXISTS ticket_sales (
            event_id TEXT PRIMARY KEY,
            date TEXT,
            tickets_sold INTEGER,
            FOREIGN KEY (event_id) REFERENCES events(id)
        );
    """)

    for event in events:
        try:
            venue = event['_embedded']['venues'][0]
            # Insert venue
            cur.execute("""
                INSERT OR IGNORE INTO venues VALUES (?, ?, ?, ?, ?, ?)
            """, (
                venue['id'],
                venue.get('name', 'Unknown'),
                venue.get('city', {}).get('name', 'Unknown'),
                venue.get('state', {}).get('stateCode', 'Unknown'),
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
            
            # Simulate ticket sales data (since actual sales data isn't available via API)
            # In a real scenario, you'd need a commerce API for actual sales numbers
            import random
            cur.execute("""
                INSERT OR IGNORE INTO ticket_sales VALUES (?, ?, ?)
            """, (
                event['id'],
                event['dates']['start'].get('localDate'),
                random.randint(50, 1000)  # Simulated data
            ))
            
        except Exception as e:
            print(f"Error storing event {event.get('id')}: {str(e)}")

    conn.commit()
    conn.close()

def main():
    # Connect to existing weather database
    db_path = 'events_weather.db'
    
    # Load cities from database
    conn = sqlite3.connect(db_path)
    cities = conn.execute("SELECT city, state FROM cities").fetchall()
    conn.close()
    
    # Process each city
    for city, state in cities[:20]:  # Limit to 20 cities for demo
        print(f"Fetching events for {city}, {state}...")
        events = fetch_events(city, state)
        if events:
            store_events(db_path, events)
        time.sleep(1)  # Respect API rate limits

if __name__ == "__main__":
    main() 
    




