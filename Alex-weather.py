
import requests

api_key = "c3adecaa2b5b7f29047c3710b51c5952"
base_url = "http://api.weatherstack.com/historical"

for day in range(1,32):
    date = f'2024-{day}-01'
    params = {
        'access_key': api_key,
        'query': 'New York',
        'historical_date': date
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    print(data)

    if response.status_code == 200:
        print("Current weather in New York City:")
        print(f"Temperature: {data['current']['temperature']}°C")
        print(f"Weather description: {data['current']['weather_descriptions'][0]}")
        print(f"Humidity: {data['current']['humidity']}%")
        print(f"Wind speed: {data['current']['wind_speed']} km/h")
        print(f"Observation time: {data['current']['observation_time']}")
    else:
        print(f"Error: {data.get('error', {}).get('info', 'Unknown error')}")