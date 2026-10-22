
import streamlit as st
import pandas as pd
import subprocess
import sys
from pathlib import Path

# -------------------------------
# 1. Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Weather Dashboard")
st.write("Weather data of Delhi, Mumbai and Banglore")

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "combined_data.csv"
MAIN_SCRIPT = PROJECT_DIR / "src" / "main.py"


# -------------------------------
# 2. Load Data
# -------------------------------
@st.cache_data
def load_data(file_path, modified_time):
    return pd.read_csv(file_path)


# -------------------------------
# 3. Refresh Weather Data
# -------------------------------
if st.button("🔄 Refresh Weather Data"):
    with st.spinner("Latest weather data is getting fetched..."):
        try:
            result = subprocess.run(
                [sys.executable, str(MAIN_SCRIPT)],
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.returncode == 0:
                st.success("Weather data successfully updated!")
                load_data.clear()
                st.rerun()
            else:
                st.error("Pipeline didn't run. Error:")
                st.code(result.stderr or result.stdout)

        except subprocess.TimeoutExpired:
            st.error(
                "took large amount of time to run a pipeline, run again."
            )
        except OSError as error:
            st.error(f"Pipeline couldn't start: {error}")


# -------------------------------
# 4. Read and Validate Data
# -------------------------------
try:
    if not DATA_FILE.exists():
        st.error(
            "data/combined_data.csv file not found. "
            "First run the pipeline."
        )
        st.stop()

    df = load_data(
        str(DATA_FILE),
        DATA_FILE.stat().st_mtime
    )

    if df.empty:
        st.warning("Currently weather data is not available.")
        st.stop()

    required_columns = {
        "time",
        "temperature_celsius",
        "relative_humidity",
        "city"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        st.error(
            "required columns are missing in CSV: "
            + ", ".join(sorted(missing_columns))
        )
        st.stop()

    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    df["temperature_celsius"] = pd.to_numeric(
        df["temperature_celsius"],
        errors="coerce"
    )

    df["relative_humidity"] = pd.to_numeric(
        df["relative_humidity"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["time", "city", "temperature_celsius"]
    )

    if df.empty:
        st.warning("Didn't find valid weather record in CSV.")
        st.stop()

    # -------------------------------
    # 5. Date Filter
    # -------------------------------
    st.subheader("📅 Filter by Date")

    min_date = df["time"].min().date()
    max_date = df["time"].max().date()

    date_range = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # -------------------------------
    # 6. City Filter
    # -------------------------------
    st.subheader("🏙️ Filter by City")

    cities = ["All Cities"] + sorted(
        df["city"].dropna().unique().tolist()
    )

    selected_city = st.selectbox(
        "Select City",
        cities
    )

    # Apply both filters
    filtered_df = df.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range

        filtered_df = filtered_df[
            (filtered_df["time"].dt.date >= start_date)
            & (filtered_df["time"].dt.date <= end_date)
        ]

    if selected_city != "All Cities":
        filtered_df = filtered_df[
            filtered_df["city"] == selected_city
        ]

    if filtered_df.empty:
        st.warning(
            "Didn't find the weather data for selected filter."
        )
        st.stop()

    # -------------------------------
    # 7. Latest Weather Cards
    # -------------------------------
    latest_df = (
        filtered_df.sort_values("time")
        .drop_duplicates(
            subset=["city"],
            keep="last"
        )
    )

    st.subheader("🌡️ Current Weather")

    columns = st.columns(len(latest_df))

    for column, (_, row) in zip(
        columns,
        latest_df.iterrows()
    ):
        with column:
            humidity = row["relative_humidity"]

            st.metric(
                label=row["city"],
                value=f'{row["temperature_celsius"]:.1f} °C',
                delta=(
                    f"Humidity: {humidity:.0f}%"
                    if pd.notna(humidity)
                    else "Humidity: N/A"
                )
            )

    # -------------------------------
    # 8. Temperature Comparison
    # -------------------------------
    st.subheader("📊 Temperature Comparison")

    temperature_chart = latest_df.set_index("city")[
        ["temperature_celsius"]
    ]

    st.bar_chart(temperature_chart)

    # -------------------------------
    # 9. Historical Temperature Trend
    # -------------------------------
    st.subheader("📈 Historical Temperature Trend")

    historical = filtered_df.sort_values("time")

    trend_chart = historical.pivot_table(
        index="time",
        columns="city",
        values="temperature_celsius",
        aggfunc="last"
    )

    st.line_chart(trend_chart)

    # -------------------------------
    # 10. Combined Data Table
    # -------------------------------
    st.subheader("📋 Combined Weather Data")
    
    st.dataframe(
    filtered_df.sort_values(
        "time",
        ascending=False
    ),
    width="stretch"
)

    

except FileNotFoundError:
    st.error(
        "data/combined_data.csv file not found. "
        "First run the pipeline."
    )

except (
    ValueError,
    KeyError,
    pd.errors.ParserError
) as error:
    st.error(
        f"Got problem in loading Data: {error}"
    )

except OSError as error:
    st.error(
        f"Got problem in reading the file: {error}"
    )
