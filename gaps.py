import numpy as np
import pandas as pd

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def load_ais(path):
    # Column names below are from NOAA MarineCadastre CSVs, as far as I know.
    # Check your file's header and adjust the rename map if they differ.
    df = pd.read_csv(path)
    df = df.rename(columns={"base_date_time": "time", "latitude": "lat", "longitude": "lon"})
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.dropna(subset=["mmsi", "time", "lat", "lon"])
    df = df[df["lat"].between(-90, 90) & df["lon"].between(-180, 180)]
    df = df.drop_duplicates(subset=["mmsi", "time"])
    return df.sort_values(["mmsi", "time"]).reset_index(drop=True)


def find_gaps(df, min_gap_minutes=30):
    g = df.groupby("mmsi", sort=False)
    out = df.rename(columns={"time": "gap_start", "lat": "start_lat",
                             "lon": "start_lon", "sog": "sog_before"})
    out["gap_end"] = g["time"].shift(-1)
    out["end_lat"] = g["lat"].shift(-1)
    out["end_lon"] = g["lon"].shift(-1)
    out = out.dropna(subset=["gap_end"])

    out["gap_minutes"] = (out["gap_end"] - out["gap_start"]).dt.total_seconds() / 60
    out = out[out["gap_minutes"] >= min_gap_minutes].copy()

    out["distance_km"] = haversine_km(out["start_lat"], out["start_lon"],
                                      out["end_lat"], out["end_lon"])
    hours = out["gap_minutes"] / 60
    out["implied_speed_kn"] = (out["distance_km"] / 1.852) / hours
    return out[["mmsi", "gap_start", "gap_end", "gap_minutes",
                "start_lat", "start_lon", "end_lat", "end_lon",
                "distance_km", "implied_speed_kn", "sog_before"]]


if __name__ == "__main__":
    df = load_ais("sample_ais.csv")
    gaps = find_gaps(df, min_gap_minutes=30)
    print(len(df), "positions,", df["mmsi"].nunique(), "vessels,", len(gaps), "gaps")
    print(gaps["gap_minutes"].describe())
    print(gaps.sort_values("gap_minutes", ascending=False).head(10))