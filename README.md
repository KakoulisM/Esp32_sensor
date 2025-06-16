# ESP32 Sensor Logger

This project collects and processes sensor data from an ESP32 device. It includes code for data acquisition, processing, and a Flask server for visualization.

---

## Project Structure

- `arduino_code/` — Arduino source files for ESP32
- `data/` — Contains sensor data logs (now compressed)
- `data_processing/` — Python scripts to clean and process data
- `db_scripts/` — Scripts to insert data into databases
- `flask_server/` — Flask app for serving the dashboard
- Other utility scripts and configuration files

---

## Data Log Compression

> ⚠️ **Important:** The sensor data log file `data/data_log.json` is now compressed as `data/data_log.zip` to reduce repository size.

### How to unzip the data log

Before running any scripts that rely on `data_log.json`, unzip the file:

#### Using Python:

```python
import zipfile

with zipfile.ZipFile("data/data_log.zip", "r") as zip_ref:
    zip_ref.extractall("data/")
