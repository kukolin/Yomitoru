"""Opciones del usuario, guardadas en settings.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path


def system_prefers_dark() -> bool:
    """True si Windows está configurado con el modo oscuro para las aplicaciones."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except OSError:
        return False


@dataclass
class Settings:
    always_on_top: bool = False
    watch_clipboard: bool = True
    dark_mode: bool = False
    bring_to_front: bool = True
    show_english: bool = True
    save_history: bool = True

    # texto de cada opción en el menú, en orden
    LABELS = {
        "watch_clipboard": "Vigilar portapapeles",
        "bring_to_front": "Mostrar la ventana al capturar",
        "always_on_top": "Siempre visible",
        "dark_mode": "Modo oscuro",
        "show_english": "Mostrar también el significado en inglés",
        "save_history": "Recordar el historial al cerrar Yomitoru",
    }

    @classmethod
    def load(cls, path: Path | None) -> Settings:
        """Lee el archivo; si no existe (primera vez) el modo oscuro sigue al de Windows."""
        if path is None or not path.is_file():
            return cls(dark_mode=system_prefers_dark())
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls(dark_mode=system_prefers_dark())
        known = {f.name for f in fields(cls)}
        return cls(**{k: bool(v) for k, v in data.items() if k in known})

    def save(self, path: Path | None) -> None:
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        except OSError:
            pass  # no poder guardar opciones no debe romper la app
