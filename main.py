# Hack for LA District Files Project
# Author: Aletia Trepte (GitHub: parcheesime)
# License: MIT – free to use, adapt, and share.

from logger import init_log, log_run, new_run_id
from datetime import datetime
import time
import os
import requests
import json
import geopandas as gpd
from shapely.geometry import shape
import geopandas as gpd
from io import StringIO
from drive_utils import drive_operations

# -------------------------------
# Configuration
# -------------------------------

# Output directory
OUTPUT_DIR = "shapefiles_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Google Drive Shared Folder IDs (from env)
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "").strip()
DRIVE_LOG_FOLDER_ID = os.getenv("DRIVE_LOG_FOLDER_ID", "").strip()

if not DRIVE_FOLDER_ID or not DRIVE_LOG_FOLDER_ID:
    raise RuntimeError("Missing required Google Drive folder IDs")

# District API endpoints (ArcGIS REST services)
API_URLS = {
    "assembly": "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/2/query?where=1%3D1&outFields=*&outSR=4326&f=json",
    "bids_city_clerk": "https://services5.arcgis.com/7nsPwEMP38bSkCjy/arcgis/rest/services/Business_Improvement_Districts/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json",
    "city_council": "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/13/query?where=1%3D1&outFields=*&outSR=4326&f=json",
    "congressional": "https://arcgis.gis.lacounty.gov/arcgis/rest/services/LACounty_Dynamic/Political_Boundaries/MapServer/2/query?where=1%3D1&outFields=*&outSR=4326&f=json",
    "neighborhood_council": "https://services5.arcgis.com/7nsPwEMP38bSkCjy/arcgis/rest/services/Neighborhood_Council_Boundaries_(2018)/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json",
    "senate": "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/23/query?where=1%3D1&outFields=*&outSR=4326&f=json",
    "supervisors": "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/4/query?where=1%3D1&outFields=*&outSR=4326&f=json",
}

# -------------------------------
# Functions
# -------------------------------

def fetch_data(url: str) -> dict:
    """Fetch raw JSON from an ArcGIS REST API."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_as_json(data: dict, filepath: str) -> None:
    """Save raw JSON data to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_as_geojson(data: dict, filepath: str) -> None:
    """Convert ArcGIS JSON to GeoJSON using GeoPandas."""
    if "features" not in data:
        print(f"[WARN] No features found in data for {filepath}")
        return

    # ArcGIS REST JSON can be read directly with GeoPandas if you stringify it
    try:
        gdf = gpd.read_file(StringIO(json.dumps(data)))
        gdf.to_file(filepath, driver="GeoJSON")
    except Exception as e:
        print(f"[ERROR] Failed to convert to GeoJSON for {filepath}: {e}")

# -------------------------------
# Main Execution
# -------------------------------

def main():
    init_log()
    run_id = new_run_id()

    for district, url in API_URLS.items():
        print(f"Fetching {district} data...")
        start = time.time()
        status_code = None
        schema_ok = False
        record_count = 0
        file_size_kb = 0
        file_written = False
        result = "fail"
        error = ""

        try:
            # Fetch data
            response = requests.get(url)
            status_code = response.status_code
            response.raise_for_status()
            data = response.json()

            # Save raw JSON
            json_path = os.path.join(OUTPUT_DIR, f"{district}.json")
            save_as_json(data, json_path)

            # Save GeoJSON
            geojson_path = os.path.join(OUTPUT_DIR, f"{district}.geojson")
            save_as_geojson(data, geojson_path)

            # Collect metadata
            schema_ok = "features" in data
            record_count = len(data.get("features", []))
            file_size_kb = round(os.path.getsize(json_path) / 1024, 2)
            file_written = True
            result = "success"

            print(f"[OK] Saved JSON: {json_path}")
            print(f"[OK] Saved GeoJSON: {geojson_path}")

            # Upload to Google Drive
            print(f"[UPLOAD] Uploading {district} files to Google Drive...")
            drive_operations.upload_file_to_drive(DRIVE_FOLDER_ID, json_path, f"{district}.json")
            drive_operations.upload_file_to_drive(DRIVE_FOLDER_ID, geojson_path, f"{district}.geojson")

        except Exception as e:
            error = str(e)
            print(f"[ERROR] Error processing {district}: {error}")

        elapsed = round(time.time() - start, 2)

        # Log this run
        entry = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "district": district,
            "url": url,
            "status_code": status_code,
            "schema_ok": schema_ok,
            "record_count": record_count,
            "file_size_kb": file_size_kb,
            "result": result,
            "error": error,
            "file_written": file_written,
            "elapsed_sec": elapsed,
        }
        log_run(entry)

    # Upload Log File
    try:
        log_path = os.path.join("logs", "run_log.csv")
        if os.path.exists(log_path):
             print(f"[UPLOAD] Uploading run_log.csv to Google Drive...")
             drive_operations.upload_file_to_drive(DRIVE_LOG_FOLDER_ID, log_path, "run_log.csv")
        else:
             print(f"[WARN] Log file not found at {log_path}, skipping upload.")
    except Exception as e:
        print(f"[ERROR] Failed to upload log file: {e}")


if __name__ == "__main__":
    main()
