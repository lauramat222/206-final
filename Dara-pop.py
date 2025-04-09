import requests
import csv
import time

base_url = "https://www.worldpop.org/rest/data/population"
iso3 = "USA"
year = "2020"
dataset = "global_age_gender_structure_2000_2020"

us_states = {
    "US-AL": "Alabama", "US-AK": "Alaska", "US-AZ": "Arizona", "US-AR": "Arkansas", "US-CA": "California",
    "US-CO": "Colorado", "US-CT": "Connecticut", "US-DE": "Delaware", "US-FL": "Florida", "US-GA": "Georgia",
    "US-HI": "Hawaii", "US-ID": "Idaho", "US-IL": "Illinois", "US-IN": "Indiana", "US-IA": "Iowa",
    "US-KS": "Kansas", "US-KY": "Kentucky", "US-LA": "Louisiana", "US-ME": "Maine", "US-MD": "Maryland",
    "US-MA": "Massachusetts", "US-MI": "Michigan", "US-MN": "Minnesota", "US-MS": "Mississippi", "US-MO": "Missouri",
    "US-MT": "Montana", "US-NE": "Nebraska", "US-NV": "Nevada", "US-NH": "New Hampshire", "US-NJ": "New Jersey",
    "US-NM": "New Mexico", "US-NY": "New York", "US-NC": "North Carolina", "US-ND": "North Dakota", "US-OH": "Ohio",
    "US-OK": "Oklahoma", "US-OR": "Oregon", "US-PA": "Pennsylvania", "US-RI": "Rhode Island", "US-SC": "South Carolina",
    "US-SD": "South Dakota", "US-TN": "Tennessee", "US-TX": "Texas", "US-UT": "Utah", "US-VT": "Vermont",
    "US-VA": "Virginia", "US-WA": "Washington", "US-WV": "West Virginia", "US-WI": "Wisconsin", "US-WY": "Wyoming"
}

output_file = "us_states_population_by_city.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["State", "City/County", "Age Group", "Sex", "Population"])

    for state_code, state_name in us_states.items():
        params = {
            "iso3": iso3,
            "year": year,
            "dataset": dataset,
            "adm0": "USA",
            "adm1": state_code,
            "format": "json"
        }

        print(f"Fetching data for {state_name} ({state_code})...")
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                for record in data["data"]:
                    age_group = record.get("age_group", "Unknown")
                    sex = record.get("sex", "Unknown")
                    population = record.get("population", "Unknown")
                    adm2 = record.get("adm2_name", "Unknown City/County")

                    writer.writerow([state_name, adm2, age_group, sex, population])
            else:
                print(f"No data found for {state_name}.")

        except Exception as e:
            print(f"Error fetching data for {state_name}: {e}")
        
        time.sleep(1)

print(f"\n Data saved to: {output_file}")
