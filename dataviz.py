import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

def plot_combined_analysis():
    """Generate all visualizations"""
    conn = sqlite3.connect('events_weather.db')
    
    # Visualization 1: Weather vs Events
    plt.figure(figsize=(15, 5))
    
    # Plot 1: Temperature vs Number of Events
    ax1 = plt.subplot(1, 3, 1)
    df_temp = pd.read_sql("""
        SELECT w.current_temp, COUNT(e.id) as event_count
        FROM weather_data w
        LEFT JOIN cities c ON w.city = c.city AND w.state = c.state
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.city, w.state
    """, conn)
    ax1.scatter(df_temp['current_temp'], df_temp['event_count'])
    ax1.set_title("Temperature vs Events")
    ax1.set_xlabel("Temperature (°F)")
    ax1.set_ylabel("Number of Events")
    
    # Plot 2: Events by Weather Condition
    ax2 = plt.subplot(1, 3, 2)
    df_conditions = pd.read_sql("""
        SELECT w.conditions, COUNT(e.id) as event_count
        FROM weather_data w
        LEFT JOIN cities c ON w.city = c.city AND w.state = c.state
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.conditions
    """, conn)
    df_conditions.plot(kind='bar', x='conditions', y='event_count', ax=ax2, legend=False)
    ax2.set_title("Events by Weather Condition")
    ax2.set_ylabel("Number of Events")
    plt.xticks(rotation=45)
    
    # Plot 3: Events by City
    ax3 = plt.subplot(1, 3, 3)
    df_cities = pd.read_sql("""
        SELECT c.city, COUNT(e.id) as event_count
        FROM cities c
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY c.city
        ORDER BY event_count DESC
        LIMIT 10
    """, conn)
    df_cities.plot(kind='bar', x='city', y='event_count', ax=ax3, legend=False)
    ax3.set_title("Top Cities by Events")
    ax3.set_ylabel("Number of Events")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('combined_analysis.png')
    plt.close()
    
    # Visualization 2: Ticket Price Analysis
    plt.figure(figsize=(10, 6))
    df_prices = pd.read_sql("""
        SELECT e.price_min, e.price_max, w.conditions
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        JOIN weather_data w ON v.city = w.city AND v.state = w.state
    """, conn)
    
    plt.scatter(df_prices['price_min'], df_prices['price_max'], c=df_prices.index)
    plt.title("Ticket Price Range by Event")
    plt.xlabel("Minimum Price ($)")
    plt.ylabel("Maximum Price ($)")
    plt.colorbar(label='Event Index')
    plt.tight_layout()
    plt.savefig('price_analysis.png')
    plt.close()
    
    conn.close()

if __name__ == "__main__":
    plot_combined_analysis()
    print("Visualizations generated: combined_analysis.png and price_analysis.png")