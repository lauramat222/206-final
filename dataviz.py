import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

def plot_ticket_sales(db_path: str = "events_weather.db"):
    """Visualize ticket sales by city and weather"""
    conn = sqlite3.connect(db_path)
    
    # Get ticket sales data joined with weather
    df = pd.read_sql("""
        SELECT 
            v.city,
            v.state,
            w.current_temp,
            w.conditions,
            SUM(t.tickets_sold) as total_tickets,
            COUNT(e.id) as num_events
        FROM ticket_sales t
        JOIN events e ON t.event_id = e.id
        JOIN venues v ON e.venue_id = v.id
        JOIN weather_data w ON v.city = w.city AND v.state = w.state
        GROUP BY v.city, v.state
    """, conn)
    
    # Create visualizations
    plt.figure(figsize=(15, 5))
    
    # Plot 1: Tickets by Temperature
    plt.subplot(1, 3, 1)
    plt.scatter(df['current_temp'], df['total_tickets'])
    plt.title("Ticket Sales vs Temperature")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Tickets Sold")
    
    # Plot 2: Tickets by Weather Condition
    plt.subplot(1, 3, 2)
    df.groupby('conditions')['total_tickets'].sum().plot(kind='bar')
    plt.title("Tickets by Weather Condition")
    plt.ylabel("Total Tickets Sold")
    plt.xticks(rotation=45)
    
    # Plot 3: Events by City
    plt.subplot(1, 3, 3)
    df.sort_values('total_tickets', ascending=False).head(10).plot(
        kind='bar', x='city', y='total_tickets', legend=False)
    plt.title("Top Cities by Ticket Sales")
    plt.ylabel("Tickets Sold")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('ticket_sales_analysis.png')
    plt.close()
    
    conn.close()