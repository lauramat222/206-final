import sqlite3

def calculate_stats(db_path: str = "updated_events_weather.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    results = {}

    # Average temperature for cities that have venues/events
    cur.execute("""
        SELECT AVG(w.current_temp)
        FROM weather_data w
        JOIN cities c ON w.city = c.city AND w.state_id = c.state_id
        JOIN venues v ON c.city = v.city AND c.state_id = v.state_id
    """)
    results['avg_temp_with_events'] = cur.fetchone()[0]

    # Event count by weather condition
    cur.execute("""
        SELECT cond.description, COUNT(e.id) as event_count
        FROM weather_data w
        JOIN cities c ON w.city = c.city AND w.state_id = c.state_id
        JOIN venues v ON c.city = v.city AND c.state_id = v.state_id
        JOIN events e ON e.venue_id = v.id
        JOIN conditions cond ON w.condition_id = cond.id
        GROUP BY cond.description
        ORDER BY event_count DESC
    """)
    results['events_by_weather'] = cur.fetchall()

    with open('calculations.txt', 'w') as f:
        f.write("WEATHER AND EVENT STATISTICS\n")
        f.write("="*40 + "\n")
        f.write(f"Average temperature in cities with events: {results['avg_temp_with_events']:.1f}\u00b0F\n\n")
        f.write("Event count by weather condition:\n")
        for condition, count in results['events_by_weather']:
            f.write(f"{condition}: {count} events\n")

    conn.close()
    return results
