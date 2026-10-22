
import pandas as pd

# Read both CSV files
weather_df = pd.read_csv("data/weather.csv")
demographics_df = pd.read_csv("data/demographics.csv")

# Weather data belongs to Delhi
weather_df["city"] = "Delhi"

# Combine data using the city column
combined_df = pd.merge(
    weather_df,
    demographics_df,
    on="city",
    how="left"
)

# Save the combined result
combined_df.to_csv("data/combined_data.csv", index=False)

print("Data combined successfully!")
print(combined_df)
print("Saved to data/combined_data.csv")
