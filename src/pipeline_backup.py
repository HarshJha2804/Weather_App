
import os
import csv
import logging
import requests

# Data folder aur log file
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    filename="data/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Cities ke coordinates
CITIES = {
    "Delhi": {"latitude": 28.6139, "longitude": 77.2090},
    "Mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "Bengaluru": {"latitude": 12.9716, "longitude": 77.5946},
}

CSV_FILE = "data/weather.csv"

FIELDS = [
    "time",
    "temperature_celsius",
    "relative_humidity",
    "city"
]


def fetch_weather(city, coordinates):
    """Open-Meteo API se city ka current weather fetch karta hai."""

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": "temperature_2m,relative_humidity_2m"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    current = data["current"]

    return {
        "time": current["time"],
        "temperature_celsius": current["temperature_2m"],
        "relative_humidity": current["relative_humidity_2m"],
        "city": city
    }


def run_pipeline():
    """Weather data fetch karke CSV mein append karta hai."""

    file_exists = os.path.exists(CSV_FILE)
    write_header = (
        not file_exists or os.path.getsize(CSV_FILE) == 0
    )

    successful_records = 0

    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)

            if write_header:
                writer.writeheader()

            for city, coordinates in CITIES.items():
                try:
                    weather = fetch_weather(city, coordinates)
                    writer.writerow(weather)
                    file.flush()

                    successful_records += 1

                    print(
                        f"{city}: weather fetched successfully "
                        f"at {weather['time']}"
                    )

                    logging.info(
                        "%s weather fetched successfully", city
                    )

                except (
                    requests.RequestException,
                    KeyError,
                    ValueError,
                    TypeError
                ):
                    logging.exception(
                        "Weather fetch failed for %s", city
                    )
                    print(f"{city}: weather fetch failed")

        if successful_records == len(CITIES):
            print("Weather CSV updated successfully!")
            logging.info(
                "Pipeline completed: %s cities processed",
                successful_records
            )
        else:
            print(
                f"Pipeline partially completed: "
                f"{successful_records}/{len(CITIES)} cities"
            )

    except OSError:
        logging.exception("Unable to write weather CSV")
        print("CSV write failed. Check data/pipeline.log")
        raise


if __name__ == "__main__":
    run_pipeline()
