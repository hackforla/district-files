# Hack for LA District Files Project
# Author: Aletia Trepte (GitHub: parcheesime)
# License: MIT – free to use, adapt, and share.

import csv
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "run_log.csv")
os.makedirs(LOG_DIR, exist_ok=True)

# Define log headers
HEADERS = [
    "run_id",
    "timestamp",
    "district",
    "url",
    "status_code",
    "schema_ok",
    "record_count",
    "file_size_kb",
    "result",
    "error",
    "file_written",
    "elapsed_sec",
]

def init_log():
    """Initialize log file with headers if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def log_run(entry: dict):
    """Append a single run entry to the log CSV."""
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(entry)

def new_run_id():
    """Generate a unique run id based on timestamp."""
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")
