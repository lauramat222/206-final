import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

def plot_combined_analysis():
    conn = sqlite3.connect('events_weather.db')

    # Set global font size for better readability
    plt.rcParams.update({'font.size': 10})

    # ========== PLOT 1: Temperature vs Number of Events ==========
    df_temp = pd.read_sql("""
        SELECT w.current_temp, COUNT(e.id) as event_count
        FROM weather_data w
        LEFT JOIN cities c ON w.city = c.city AND w.state = c.state
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.city, w.state
    """, conn)

    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    axs[0].scatter(df_temp['current_temp'], df_temp['event_count'], alpha=0.7, edgecolors='k')
    axs[0].set_title("Temperature vs Number of Events")
    axs[0].set_xlabel("Temperature (°F)")
    axs[0].set_ylabel("Number of Events")
    axs[0].grid(True)

    # ========== PLOT 2: Events by Weather Condition ==========
    df_conditions = pd.read_sql("""
        SELECT w.conditions, COUNT(e.id) as event_count
        FROM weather_data w
        LEFT JOIN cities c ON w.city = c.city AND w.state = c.state
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.conditions
    """, conn)

    df_conditions.sort_values(by='event_count', ascending=False, inplace=True)
    axs[1].bar(df_conditions['conditions'], df_conditions['event_count'], color='skyblue', edgecolor='black')
    axs[1].set_title("Events by Weather Condition")
    axs[1].set_ylabel("Number of Events")
    axs[1].tick_params(axis='x', rotation=45)
    axs[1].grid(axis='y')

    # Add labels to each bar
    for i, count in enumerate(df_conditions['event_count']):
        axs[1].text(i, count + 1, str(count), ha='center', va='bottom', fontsize=8)

    # ========== PLOT 3: Top Cities by Events ==========
    df_cities = pd.read_sql("""
        SELECT c.city, COUNT(e.id) as event_count
        FROM cities c
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY c.city
        ORDER BY event_count DESC
        LIMIT 10
    """, conn)

    axs[2].bar(df_cities['city'], df_cities['event_count'], color='lightgreen', edgecolor='black')
    axs[2].set_title("Top 10 Cities by Event Count")
    axs[2].set_ylabel("Number of Events")
    axs[2].tick_params(axis='x', rotation=45)
    axs[2].grid(axis='y')

    for i, count in enumerate(df_cities['event_count']):
        axs[2].text(i, count + 1, str(count), ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig("combined_analysis.png")
    plt.close()

    # ========== SCATTER PLOT: Ticket Price Range ==========
    df_prices = pd.read_sql("""
        SELECT e.price_min, e.price_max, w.conditions
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        JOIN weather_data w ON v.city = w.city AND v.state = w.state
    """, conn)

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        df_prices['price_min'],
        df_prices['price_max'],
        c=range(len(df_prices)),  # just a gradient
        cmap='viridis',
        alpha=0.6,
        edgecolors='k'
    )
    plt.title("Ticket Price Range by Event")
    plt.xlabel("Minimum Price ($)")
    plt.ylabel("Maximum Price ($)")
    plt.grid(True)
    plt.colorbar(scatter, label="Event Index")
    plt.tight_layout()
    plt.savefig("price_analysis.png")
    plt.close()

    conn.close()
    print("Improved visualizations saved as 'combined_analysis.png' and 'price_analysis.png'")

if __name__ == "__main__":
    plot_combined_analysis()