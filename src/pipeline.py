import requests
import csv
import os

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "current": "temperature_2m,relative_humidity_2m",
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json()
weather = data["current"]

os.makedirs("data", exist_ok=True)

with open("data/weather.csv", "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "time",
        "temperature_celsius",
        "relative_humidity"
    ])

    writer.writerow([
        weather["time"],
        weather["temperature_2m"],
        weather["relative_humidity_2m"]
    ])

print("Weather data CSV mein save ho gaya!")
print("File location: data/weather.csv")