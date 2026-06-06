# src/expense_tracker/config/settings.py
# Defines runtime configuration for local JSON expense storage.
# Connects to: src/expense_tracker/services/storage.py
# Created: 2026-06-06

from pathlib import Path
import os

DEFAULT_DATA_FILE = Path("data") / "expenses.json"
DATA_FILE_ENV_VAR = "EXPENSE_TRACKER_DATA_FILE"


def get_data_file_path() -> Path:
    """Return the configured JSON data file path."""
    configured_path = os.getenv(DATA_FILE_ENV_VAR, "").strip()
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DATA_FILE
