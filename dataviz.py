import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

def plot_combined_analysis():
    conn = sqlite3.connect('events_weather.db')
    plt.rcParams.update({'font.size': 10})  # improve readability

    # ========== PLOT 1: Temperature vs Events ==========
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
    for i, count in enumerate(df_conditions['event_count']):
        axs[1].text(i, count + 1, str(count), ha='center', va='bottom', fontsize=8)

    # ========== PLOT 3: Top Cities by Event Count ==========
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
    axs[2].set_title("Top 10 Cities by Events")
    axs[2].set_ylabel("Number of Events")
    axs[2].tick_params(axis='x', rotation=45)
    axs[2].grid(axis='y')
    for i, count in enumerate(df_cities['event_count']):
        axs[2].text(i, count + 1, str(count), ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig("combined_analysis.png")
    plt.close()