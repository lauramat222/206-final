import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import textwrap

def wrap_labels(labels, width=15):
    return ['\n'.join(textwrap.wrap(label, width)) for label in labels]

def plot_combined_analysis():
    conn = sqlite3.connect('events_weather.db')
    plt.rcParams.update({'font.size': 10})  # Better default font size

    # ========== FIGURE 1: Combined Analysis ==========
    df_temp = pd.read_sql("""
        SELECT w.current_temp, COUNT(e.id) as event_count
        FROM weather_data w
        LEFT JOIN cities c ON w.city = c.city AND w.state = c.state
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.city, w.state
    """, conn)

    df_conditions = pd.read_sql("""
        SELECT w.conditions, COUNT(e.id) as event_count
        FROM weather_data w
        LEFT JOIN cities c ON w.city = c.city AND w.state = c.state
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.conditions
    """, conn)

    df_cities = pd.read_sql("""
        SELECT c.city, COUNT(e.id) as event_count
        FROM cities c
        LEFT JOIN venues v ON v.city = c.city AND v.state = c.state
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY c.city
        ORDER BY event_count DESC
        LIMIT 10
    """, conn)

    fig, axs = plt.subplots(1, 3, figsize=(22, 6))

    # Scatter plot: Temp vs Events
    axs[0].scatter(df_temp['current_temp'], df_temp['event_count'], alpha=0.7, edgecolors='k')
    axs[0].set_title("Temperature vs Events")
    axs[0].set_xlabel("Temperature (°F)")
    axs[0].set_ylabel("Number of Events")
    axs[0].grid(True)

    # Bar chart: Weather Condition
    df_conditions.sort_values(by='event_count', ascending=False, inplace=True)
    axs[1].bar(wrap_labels(df_conditions['conditions']), df_conditions['event_count'], color='skyblue', edgecolor='black')
    axs[1].set_title("Events by Weather Condition")
    axs[1].set_ylabel("Number of Events")
    axs[1].tick_params(axis='x', rotation=45)
    axs[1].grid(axis='y')

    # Bar chart: Top Cities
    axs[2].bar(df_cities['city'], df_cities['event_count'], color='lightgreen', edgecolor='black')
    axs[2].set_title("Top Cities by Events")
    axs[2].set_ylabel("Number of Events")
    axs[2].tick_params(axis='x', rotation=45)
    axs[2].grid(axis='y')

    plt.tight_layout()
    plt.savefig("combined_analysis.png")
    plt.close()

    # ========== FIGURE 2: Price Scatter or Fallback Bar ==========
    df_prices = pd.read_sql("""
        SELECT e.price_min, e.price_max, w.conditions
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        JOIN weather_data w ON v.city = w.city AND v.state = w.state
        WHERE e.price_min IS NOT NULL AND e.price_max IS NOT NULL
    """, conn)

    if df_prices.empty:
        print("No valid price data found. Plotting fallback bar chart.")

        fallback_df = pd.read_sql("""
            SELECT w.conditions, AVG(e.price_min) as avg_min, AVG(e.price_max) as avg_max
            FROM events e
            JOIN venues v ON e.venue_id = v.id
            JOIN weather_data w ON v.city = w.city AND v.state = w.state
            WHERE e.price_min IS NOT NULL AND e.price_max IS NOT NULL
            GROUP BY w.conditions
        """, conn)

        fallback_df.sort_values(by='avg_max', ascending=False, inplace=True)
        print("\nFallback data preview:")
        print(fallback_df.head())
        print(fallback_df.dtypes)
        fallback_df['avg_min'] = pd.to_numeric(fallback_df['avg_min'], errors='coerce')
        fallback_df['avg_max'] = pd.to_numeric(fallback_df['avg_max'], errors='coerce')
        fallback_df.dropna(subset=['avg_min', 'avg_max'], how='all', inplace=True)

        if fallback_df.empty:
            print("⚠️ Still no usable numeric price data to plot. Exiting price_analysis.")
            return

        fallback_df.plot(
            kind='bar',
            x='conditions',
            y=['avg_min', 'avg_max'],
            figsize=(12, 6),
            edgecolor='black',
            color=['#4caf50', '#f44336']
        )
        
        plt.title("Average Ticket Prices by Weather Condition")
        plt.ylabel("Average Price ($)")
        plt.xticks(ticks=np.arange(len(fallback_df['conditions'])), labels=wrap_labels(fallback_df['conditions']), rotation=45)
        plt.tight_layout()
        plt.savefig("price_analysis.png")
        plt.close()
    else:
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(
            df_prices['price_min'],
            df_prices['price_max'],
            c=range(len(df_prices)),
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

if __name__ == "__main__":
    plot_combined_analysis()