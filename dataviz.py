import sqlite3
import matplotlib.pyplot as plt
print(plt.style.available)
import pandas as pd
pd.set_option('future.no_silent_downcasting', True) 
import numpy as np
import textwrap
from matplotlib.ticker import MaxNLocator
from scipy.stats import linregress
df = pd.read_csv('top_100_us_cities_lat_lon.csv')
print(df.head())
print(df.dtypes)

def wrap_labels(labels, width=15):
    """Helper to wrap long labels"""
    return ['\n'.join(textwrap.wrap(label, width)) for label in labels]

def plot_dual_axis_trends():
    # Connect to your SQLite database
    conn = sqlite3.connect('updated_events_weather.db')  # Make sure this matches your DB filename

    query = """
    SELECT 
        e.date,
        AVG(w.current_temp) as avg_temp,
        COUNT(e.id) as event_count
    FROM events e  
    JOIN venues v ON e.venue_id = v.id
    JOIN cities c ON v.city = c.city AND v.state = c.state  -- Changed from state_id
    JOIN weather_data w ON w.city = c.city AND w.state = c.state
    WHERE e.date IS NOT NULL
    GROUP BY e.date
    ORDER BY e.date
    """
    
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    
    # Convert date to datetime and sort
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)
    
    # Create figure and primary axis
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot temperature on primary axis
    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°F)', color=color)
    temp_line = ax1.plot(df['date'], df['avg_temp'], 
                        color=color, 
                        marker='o', 
                        linestyle='-',
                        label='Temperature')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    # Create secondary axis for event count
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Number of Events', color=color)
    event_line = ax2.plot(df['date'], df['event_count'], 
                         color=color, 
                         marker='s', 
                         linestyle='--',
                         label='Events')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Add legend
    lines = temp_line + event_line
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    # Format x-axis
    plt.gcf().autofmt_xdate()
    ax1.xaxis.set_major_locator(MaxNLocator(10))  # Limit number of x-ticks
    
    plt.title('Temperature vs Event Count Over Time')
    plt.tight_layout()
    plt.savefig("dual_axis_trends.png", dpi=300, bbox_inches='tight')
    plt.close()
    conn.close()
    print("Saved dual_axis_trends.png")

def plot_weather_sales_correlation():
    """Scatter plot with trendline for weather vs ticket sales"""
    conn = sqlite3.connect('events_weather.db')
    
    # Get weather vs sales data
    df = pd.read_sql("""
        SELECT 
            w.current_temp,
            COUNT(e.id) as event_count,
            AVG(e.price_max) as avg_price
        FROM weather_data w
        JOIN cities c ON w.city = c.city AND w.state_id = c.state_id
        LEFT JOIN venues v ON v.city = c.city AND v.state_id = c.state_id
        LEFT JOIN events e ON e.venue_id = v.id
        GROUP BY w.city, w.state
    """, conn)
    
    if df.empty or len(df) < 3:
        print("Not enough data for correlation plot")
        conn.close()
        return
    
    # Calculate regression
    slope, intercept, r_value, p_value, std_err = linregress(
        df['current_temp'], df['event_count'])
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Scatter plot
    scatter = plt.scatter(
        df['current_temp'], 
        df['event_count'],
        c=df['avg_price'].fillna(0).astype(float),
        cmap='viridis',
        alpha=0.7,
        edgecolors='w',
        s=100,
        label='City Data'
    )
    
    # Trendline
    plt.plot(df['current_temp'], 
             intercept + slope * df['current_temp'], 
             'r--',
             label=f'Trendline (R²={r_value**2:.2f})')
    
    # Formatting
    plt.title('Temperature vs Event Count Correlation')
    plt.xlabel('Temperature (°F)')
    plt.ylabel('Number of Events')
    plt.grid(True, alpha=0.3)
    
    # Colorbar for price
    cbar = plt.colorbar(scatter)
    cbar.set_label('Average Ticket Price ($)')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig("weather_sales_correlation.png", dpi=300, bbox_inches='tight')
    plt.close()
    conn.close()
    print("Saved weather_sales_correlation.png")

def plot_combined_analysis():
    """Main visualization function (updated with cleaner formatting)"""
    conn = sqlite3.connect('events_weather.db')
    
    # Set global style parameters
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.titlesize': 16
    })
    
    # [Rest of your existing plot_combined_analysis code...]
    # Make sure to add similar formatting improvements to your existing plots
    
    conn.close()

if __name__ == "__main__":
    plot_dual_axis_trends()
    plot_weather_sales_correlation()
    plot_combined_analysis()




    import sqlite3
    conn = sqlite3.connect('events_weather.db')
    df = pd.read_sql("SELECT date FROM events WHERE date IS NOT NULL", conn)
    print(df.head())
    print(f"Total dates: {len(df)}")
    conn.close()

