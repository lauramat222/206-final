import requests
from bs4 import BeautifulSoup

url = "https://www.fittotravel.net/latitude-and-longitude-of-u-s-largest-cities"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")

city_data = []

for row in table.find_all("tr")[1:]:
    cols = row.find_all("td")
    if len(cols) >= 4:
        city = cols[0].get_text(strip=True)
        state = cols[1].get_text(strip=True)
        latitude = cols[2].get_text(strip=True)
        longitude = cols[3].get_text(strip=True)
        city_data.append({
            "city": city,
            "state": state,
            "latitude": latitude,
            "longitude": longitude
        })

for entry in city_data[:10]:
    print(entry)

import csv

with open("top_100_us_cities_lat_lon.csv", "w", newline="") as csvfile:
    fieldnames = ["city", "state", "latitude", "longitude"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data in city_data:
        writer.writerow(data)
