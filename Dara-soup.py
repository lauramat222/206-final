import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

url = "https://www.fittotravel.net/latitude-and-longitude-of-u-s-largest-cities"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")
if not table:
    print("No table found on the page. The website structure may have changed.")
    exit()

city_data = []

for row in table.find_all("tr")[1:]:
    cols = row.find_all("td")
    if len(cols) >= 4:
        city = cols[1].get_text(strip=True)
        state = cols[2].get_text(strip=True)
        latitude = cols[3].get_text(strip=True)
        longitude = cols[4].get_text(strip=True)
        city_data.append({
            "city": city,
            "state": state,
            "latitude": latitude,
            "longitude": longitude
        })

for entry in city_data[:100]:
    print(entry)

import csv

with open("top_100_us_cities_lat_lon.csv", "w", newline="") as csvfile:
    fieldnames = ["city", "state", "latitude", "longitude"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data in city_data:
        writer.writerow(data)

