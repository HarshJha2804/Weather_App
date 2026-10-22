import pandas as pd

# Read Excel file
df = pd.read_excel("Global demographic dataset .xlsx")

# Clean column names
df.columns = df.columns.str.strip()

# Create cities.csv
cities = df[
    ["City", "Country", "Latitude", "Longitude"]
].copy()

cities.columns = [
    "city", "country", "latitude", "longitude"
]

cities.to_csv("data/cities.csv", index=False)

# Create demographics.csv
demographics = df[["City", "Population"]].copy()

demographics.columns = ["city", "population"]
demographics["median_age"] = None

demographics.to_csv("data/demographics.csv", index=False)

print("Dataset files created successfully!")
print("Total cities:", len(cities))
print("Cities file:", cities.shape)
print("Demographics file:", demographics.shape)
