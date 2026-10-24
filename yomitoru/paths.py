"""Data paths, for both normal runs and PyInstaller builds."""

import os
import sys
from pathlib import Path

DB_NAME = "kanjidic2.sqlite"


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    return project_root() / "data"


def config_dir() -> Path:
    """User folder for settings and history (%APPDATA%\\Yomitoru)."""
    base = os.environ.get("APPDATA")
    return Path(base) / "Yomitoru" if base else Path.home() / ".yomitoru"


def find_db() -> Path | None:
    """Find the database: first next to the .exe / project, then inside the bundle."""
    candidates = [data_dir() / DB_NAME]
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        candidates.append(Path(bundle) / "data" / DB_NAME)
    for path in candidates:
        if path.is_file():
            return path
    return None
