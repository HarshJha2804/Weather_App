
import logging
import pandas as pd

logging.basicConfig(
    filename="data/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    weather_df = pd.read_csv("data/weather.csv")
    demographics_df = pd.read_csv("data/demographics.csv")

    required_weather = {
        "time",
        "temperature_celsius",
        "relative_humidity",
        "city"
    }

    required_demo = {
        "city",
        "population",
        "median_age"
    }

    if not required_weather.issubset(weather_df.columns):
        raise ValueError("Weather CSV mein required columns missing hain")

    if not required_demo.issubset(demographics_df.columns):
        raise ValueError("Demographics CSV mein required columns missing hain")

    # Same city aur same timestamp ki duplicate readings hatao
    weather_df = weather_df.drop_duplicates(
        subset=["city", "time"],
        keep="last"
    )

    # Weather aur demographic data join karo
    combined_df = pd.merge(
        weather_df,
        demographics_df,
        on="city",
        how="left",
        validate="many_to_one"
    )

    if combined_df["population"].isna().any():
        raise ValueError("Kuch cities ka demographic data nahi mila")

    # Latest readings ko upar dikhane ke liye sort karo
    combined_df = combined_df.sort_values(
        by="time",
        ascending=False
    )

    combined_df.to_csv(
        "data/combined_data.csv",
        index=False
    )

    logging.info(
        "Transformation successful: %s unique records",
        len(combined_df)
    )

    print("Weather and demographic data combined!")
    print(combined_df)
    print("Saved to data/combined_data.csv")

except (
    OSError,
    ValueError,
    pd.errors.ParserError,
    pd.errors.EmptyDataError
):
    logging.exception("Data transformation failed")
    print("Transformation failed. Check data/pipeline.log")
    raise
