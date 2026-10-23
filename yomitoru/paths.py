"""Rutas de datos, compatibles con ejecución normal y con PyInstaller."""

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
    """Carpeta del usuario para opciones e historial (%APPDATA%\\Yomitoru)."""
    base = os.environ.get("APPDATA")
    return Path(base) / "Yomitoru" if base else Path.home() / ".yomitoru"


def find_db() -> Path | None:
    """Busca la base: primero junto al .exe / proyecto, después dentro del bundle."""
    candidates = [data_dir() / DB_NAME]
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        candidates.append(Path(bundle) / "data" / DB_NAME)
    for path in candidates:
        if path.is_file():
            return path
    return None
