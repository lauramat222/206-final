import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from typing import List

def plot_weather_vs_events(db_path: str = "ticketmaster_events.db"):
    """Create visualization comparing weather and events"""
    conn = sqlite3.connect(db_path)
    
    # Get weather data
    weather_df = pd.read_sql("""
        SELECT city, state, current_temp, conditions 
        FROM weather_data
    """, conn)
    
    # Get event counts
    events_df = pd.read_sql("""
        SELECT v.city, v.state, COUNT(e.id) as event_count
        FROM events e
        JOIN venues v ON e.venue_id = v.venue_id
        GROUP BY v.city, v.state
    """, conn)
    
    # Merge data
    merged = pd.merge(weather_df, events_df, on=['city', 'state'])
    
    # Create figure
    plt.figure(figsize=(12, 6))
    
    # Plot 1: Temperature vs Events
    plt.subplot(1, 2, 1)
    plt.scatter(merged['current_temp'], merged['event_count'])
    plt.title("Temperature vs Number of Events")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Number of Events")
    
    # Plot 2: Weather Conditions vs Events
    plt.subplot(1, 2, 2)
    merged['conditions'].value_counts().plot(kind='bar')
    plt.title("Events by Weather Condition")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('weather_events_analysis.png')
    plt.close()
    
    conn.close()

def plot_event_genres(db_path: str = "ticketmaster_events.db"):
    """Create visualization of event genres"""
    conn = sqlite3.connect(db_path)
    
    df = pd.read_sql("""
        SELECT genre, COUNT(*) as count 
        FROM events 
        WHERE genre IS NOT NULL
        GROUP BY genre
        ORDER BY count DESC
        LIMIT 10
    """, conn)
    
    plt.figure(figsize=(10, 6))
    df.plot(kind='bar', x='genre', y='count', legend=False)
    plt.title("Top 10 Event Genres")
    plt.xlabel("Genre")
    plt.ylabel("Number of Events")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('event_genres.png')
    plt.close()
    
    conn.close()