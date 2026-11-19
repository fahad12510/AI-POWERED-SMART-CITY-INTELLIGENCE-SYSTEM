from pathlib import Path
import csv
import io
import numpy as np

DATA_DIR = Path(__file__).parent / "data"
SAMPLE_FILE = DATA_DIR / "sample_city_data.csv"
CURRENT_FILE = DATA_DIR / "current_city_data.csv"
REQUIRED = {"location", "day", "traffic", "aqi"}

def load_dataset():
    path = CURRENT_FILE if CURRENT_FILE.exists() else SAMPLE_FILE
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    locations = list(dict.fromkeys(row["location"] for row in rows))
    days = sorted({int(row["day"]) for row in rows})
    traffic, aqi = [], []
    for location in locations:
        subset = {int(r["day"]): r for r in rows if r["location"] == location}
        if len(subset) != len(days) or any(day not in subset for day in days):
            raise ValueError("Every location must contain readings for the same days.")
        traffic.append([float(subset[d]["traffic"]) for d in days])
        aqi.append([float(subset[d]["aqi"]) for d in days])
    return {"locations": locations, "traffic": traffic, "aqi": aqi,
            "days": days, "is_sample": path == SAMPLE_FILE}

def _validate_rows(rows):
    if not rows or not REQUIRED.issubset(set(rows[0].keys())):
        raise ValueError("CSV must contain columns: location, day, traffic, aqi.")
    seen = set()
    locations, days = set(), set()
    for row in rows:
        try:
            name = row["location"].strip()
            day = int(row["day"])
            traffic, aqi = float(row["traffic"]), float(row["aqi"])
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Missing or non-numeric values found. Check every row.")
        if not name or day < 1 or traffic < 0 or aqi < 0 or not np.isfinite(traffic + aqi):
            raise ValueError("Values must be valid, finite and non-negative.")
        key = (name, day)
        if key in seen:
            raise ValueError("Duplicate location/day records are not allowed.")
        seen.add(key); locations.add(name); days.add(day)
    expected = len(locations) * len(days)
    if len(rows) != expected:
        raise ValueError("Dataset has missing location/day readings. Missing values are not replaced with zero.")

def save_uploaded_csv(file):
    if not file.filename.lower().endswith(".csv"):
        raise ValueError("Only CSV files are supported.")
    raw = file.read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    _validate_rows(rows)
    DATA_DIR.mkdir(exist_ok=True)
    with CURRENT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["location","day","traffic","aqi"])
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})

def restore_sample():
    if CURRENT_FILE.exists():
        CURRENT_FILE.unlink()
