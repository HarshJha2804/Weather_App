
import logging
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

logging.basicConfig(
    filename=DATA_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def transform_data():
    weather_df = pd.read_csv(DATA_DIR / "weather.csv")
    demographics_df = pd.read_csv(DATA_DIR / "demographics.csv")

    required_weather = {
        "time", "temperature_celsius",
        "relative_humidity", "city"
    }
    required_demo = {"city", "population", "median_age"}

    if not required_weather.issubset(weather_df.columns):
        raise ValueError("Weather CSV mein required columns missing hain")

    if not required_demo.issubset(demographics_df.columns):
        raise ValueError("Demographics CSV mein required columns missing hain")

    # City names ko consistent rakho
    weather_df["city"] = weather_df["city"].astype(str).str.strip()
    demographics_df["city"] = demographics_df["city"].astype(str).str.strip()

    # Same city aur timestamp ki duplicate readings hatao
    weather_df = weather_df.drop_duplicates(
        subset=["city", "time"],
        keep="last"
    )

    # Weather ki sabhi cities preserve hongi
    combined_df = pd.merge(
        weather_df,
        demographics_df,
        on="city",
        how="left",
        validate="many_to_one"
    )

    # Missing demographics ko NaN hi rakho; fake values mat bharo
    combined_df = combined_df.sort_values(
        by="time",
        ascending=False
    )

    output_file = DATA_DIR / "combined_data.csv"
    combined_df.to_csv(output_file, index=False)

    print("Transformation successful!")
    print("Total rows:", len(combined_df))
    print("Unique cities:", combined_df["city"].nunique())
    print(
        "Cities with missing population:",
        combined_df.loc[
            combined_df["population"].isna(), "city"
        ].nunique()
    )
    print("Saved to:", output_file)

if __name__ == "__main__":
    try:
        transform_data()
    except (OSError, ValueError, pd.errors.ParserError):
        logging.exception("Data transformation failed")
        raise

