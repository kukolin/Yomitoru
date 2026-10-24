"""User settings, saved in settings.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from .i18n import DEFAULT_LANGUAGE, LANGUAGES


def system_prefers_dark() -> bool:
    """True if Windows is set to dark mode for apps."""
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
    watch_clipboard: bool = True
    bring_to_front: bool = True
    open_jisho: bool = False
    always_on_top: bool = False
    dark_mode: bool = False
    language: str = "en"

    # toggles in the Options menu, in order (setting name -> i18n text key)
    TOGGLES = {
        "bring_to_front": "opt_bring_to_front",
        "open_jisho": "opt_open_jisho",
        "always_on_top": "opt_always_on_top",
        "dark_mode": "opt_dark_mode",
    }

    @classmethod
    def first_run(cls) -> Settings:
        """Initial values: English, and the theme follows Windows."""
        return cls(dark_mode=system_prefers_dark(), language=DEFAULT_LANGUAGE)

    @classmethod
    def load(cls, path: Path | None) -> Settings:
        if path is None or not path.is_file():
            return cls.first_run()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls.first_run()
        settings = cls.first_run()
        for f in fields(cls):
            value = data.get(f.name)
            if isinstance(value, type(getattr(settings, f.name))):  # ignore invalid types
                setattr(settings, f.name, value)
        if settings.language not in LANGUAGES:
            settings.language = DEFAULT_LANGUAGE
        return settings

    def save(self, path: Path | None) -> None:
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        except OSError:
            pass  # failing to save settings must not break the app
