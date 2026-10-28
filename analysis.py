"""Easy Pandas functions for historical Indian AQI data."""
from pathlib import Path
import pandas as pd

# These are based on calendar months, not the weather on a particular day.
SEASONS = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon"
}
SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]


def load_data(filename):
    """Read the real Kaggle CSV and clean common missing/invalid values."""
    if not Path(filename).is_file():
        raise FileNotFoundError("Historical CSV not found. Click 'Import CSV'.")

    data = pd.read_csv(filename, low_memory=False)
    data.columns = data.columns.str.strip()
    required = {"City", "Date", "AQI"}
    if not required.issubset(data.columns):
        raise ValueError("Please select a CSV containing City, Date and AQI columns.")

    data["City"] = data["City"].astype("string").str.strip()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["City", "Date"]).copy()
    data = data[data["City"] != ""].copy()

    for name in ["AQI", "PM2.5", "PM10"]:
        if name not in data.columns:
            data[name] = float("nan")
        data[name] = pd.to_numeric(data[name], errors="coerce")
        data.loc[data[name] < 0, name] = float("nan")

    data["Month"] = data["Date"].dt.month
    data["YearMonth"] = data["Date"].dt.strftime("%Y-%m")
    data["Season"] = data["Month"].map(SEASONS)
    return data


def city_data(data, city):
    """Keep only the rows for the chosen city."""
    return data[data["City"] == city]


def city_summary(data, city):
    """Return mean AQI, worst month and the season with highest mean AQI."""
    rows = city_data(data, city)
    mean_aqi = rows["AQI"].mean()

    # For a fairer monthly result, require at least five valid daily readings.
    months = rows.groupby("YearMonth")["AQI"].agg(["mean", "count"])
    months = months[months["count"] >= 5]
    worst = str(months["mean"].idxmax()) if not months.empty else "N/A"

    seasons = rows.groupby("Season")["AQI"].mean().dropna()
    season = str(seasons.idxmax()) if not seasons.empty else "N/A"
    return mean_aqi, worst, season, int(rows["AQI"].count())


def month_averages(data, city):
    """Average AQI in January, February ... December across available years."""
    return city_data(data, city).groupby("Month")["AQI"].mean().reindex(range(1, 13))


def season_averages(data, city):
    """Four-season mean AQI for the selected city."""
    return city_data(data, city).groupby("Season")["AQI"].mean().reindex(SEASON_ORDER)
