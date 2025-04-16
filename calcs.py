import sqlite3
from typing import Tuple, List

def calculate_stats(db_path: str = "events_weather.db"):
    """Calculate statistics from the database"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    results = {}

    cur.execute("""
        SELECT AVG(w.current_temp)
        FROM weather_data w
        JOIN cities c ON w.city = c.city AND w.state = c.state
        WHERE EXISTS (
            SELECT 1 FROM venues v 
            WHERE v.city = c.city AND v.state = c.state
        )
    """)
    results['avg_temp_with_events'] = cur.fetchone()[0]
    
    cur.execute("""
        SELECT w.conditions, COUNT(e.id) as event_count
        FROM weather_data w
        JOIN cities c ON w.city = c.city AND w.state = c.state
        JOIN venues v ON v.city = c.city AND v.state = c.state
        JOIN events e ON e.venue_id = v.venue_id
        GROUP BY w.conditions
        ORDER BY event_count DESC
    """)
    results['events_by_weather'] = cur.fetchall()
    
    with open('calculations.txt', 'w') as f:
        f.write("WEATHER AND EVENT STATISTICS\n")
        f.write("="*40 + "\n")
        f.write(f"Average temperature in cities with events: {results['avg_temp_with_events']:.1f}°F\n\n")
        f.write("Event count by weather condition:\n")
        for condition, count in results['events_by_weather']:
            f.write(f"{condition}: {count} events\n")
    
    conn.close()
    return results