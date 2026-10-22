
from pathlib import Path
import logging
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CITIES_FILE = DATA_DIR / "cities.csv"
WEATHER_FILE = DATA_DIR / "weather.csv"
LOG_FILE = DATA_DIR / "pipeline.log"

API_URL = "https://api.open-meteo.com/v1/forecast"

DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def fetch_weather(city):
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": "temperature_2m,relative_humidity_2m",
        "timezone": "GMT",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    weather = response.json()
    current = weather.get("current", {})

    return {
        "time": current.get("time"),
        "temperature_celsius": current.get("temperature_2m"),
        "relative_humidity": current.get("relative_humidity_2m"),
        "city": city["city"],
        "country": city["country"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
    }


def run_pipeline():
    cities = pd.read_csv(CITIES_FILE)
    records = []

    for _, city in cities.iterrows():
        try:
            record = fetch_weather(city)
            records.append(record)
            print(f"Fetched: {city['city']}, {city['country']}")
        except (requests.RequestException, ValueError, KeyError) as exc:
            logging.exception("Failed for %s: %s", city["city"], exc)
            print(f"Failed: {city['city']} - {exc}")

    if not records:
        raise RuntimeError("No weather data fetched. Check internet and API.")

    new_data = pd.DataFrame(records)

    if WEATHER_FILE.exists():
        old_data = pd.read_csv(WEATHER_FILE)
        combined = pd.concat([old_data, new_data], ignore_index=True)
    else:
        combined = new_data

    combined = combined.drop_duplicates(
        subset=["city", "country", "time"],
        keep="last",
    )

    combined.to_csv(WEATHER_FILE, index=False)

    logging.info("Fetched weather for %s cities", len(new_data))
    print(f"\nSuccess! Fetched weather for {len(new_data)} cities.")
    print(f"Saved to: {WEATHER_FILE}")


if __name__ == "__main__":
    run_pipeline()

