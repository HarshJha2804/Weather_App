
import pandas as pd


def test_weather_data_has_required_columns():
    df = pd.DataFrame({
        "time": ["2026-10-22T10:00"],
        "temperature_celsius": [30.5],
        "relative_humidity": [60],
        "city": ["Delhi"]
    })

    required_columns = {
        "time",
        "temperature_celsius",
        "relative_humidity",
        "city"
    }

    assert required_columns.issubset(df.columns)


def test_duplicate_weather_records():
    df = pd.DataFrame({
        "city": ["Delhi", "Delhi"],
        "time": ["2026-10-22T10:00", "2026-10-22T10:00"],
        "temperature_celsius": [30.5, 30.5]
    })

    result = df.drop_duplicates(
        subset=["city", "time"],
        keep="last"
    )

    assert len(result) == 1
