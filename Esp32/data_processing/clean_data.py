import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
data_log_path = Path(LOG_FILE_PATH)
json_path = BASE_DIR / "Cleaned_data.json"
csv_path = BASE_DIR / "Cleaned_data.csv"
entry_path = BASE_DIR / "Entry.json"

def load_valid_json_lines(filepath):
    data = []
    with filepath.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Skipping line {line_num}: {e}")
    return pd.DataFrame(data)

if not data_log_path.exists():
    raise FileNotFoundError(f"File not found: {data_log_path}")

stats_df = load_valid_json_lines(data_log_path)

stats_df["timestamp"] = stats_df["timestamp"].astype(str)
stats_df[["date", "time"]] = stats_df["timestamp"].str.split(' ', expand=True)
stats_df = stats_df.join(pd.json_normalize(stats_df["data"]))
stats_df.drop(columns=["timestamp", "data"], inplace=True)
stats_df["minutes"] = stats_df["time"].str[:5]

df_filtered = stats_df[stats_df["minutes"].str[-2:].astype(int) % 10 == 0]

df_grouped = df_filtered.groupby(["date", "minutes"]).agg({
    "humidity": "mean",
    "temperature_c": "mean"
}).round(2).reset_index()

if json_path.exists():
    with json_path.open("r", encoding="utf-8") as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    df_existing = pd.DataFrame(existing_data)
else:
    df_existing = pd.DataFrame(columns=["date", "minutes", "humidity", "temperature_c"])

merged = pd.merge(df_grouped, df_existing[["date", "minutes"]], on=["date", "minutes"], how="left", indicator=True)
df_new = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

if not df_new.empty:
    df_updated = pd.concat([df_existing, df_new], ignore_index=True)
    df_updated.sort_values(["date", "minutes"], inplace=True)
    df_updated.to_json(json_path, orient="records", indent=2)
    df_updated.to_csv(csv_path, index=False)
    print(f"{len(df_new)} new entries added to cleaned files.")
else:
    print("No new entries to add — cleaned files are up to date.")

try:
    with entry_path.open("r", encoding="utf-8") as infile:
        data_list = json.load(infile)
except (FileNotFoundError, json.JSONDecodeError):
    data_list = []

timestamped_data = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'data': "Data Added"
}
data_list.append(timestamped_data)

with entry_path.open("w", encoding="utf-8") as outfile:
    json.dump(data_list, outfile, indent=2)

print("New entry added successfully to log.")
