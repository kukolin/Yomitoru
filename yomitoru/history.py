"""Historial de búsquedas con navegación atrás/adelante, guardado en history.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

MAX_ENTRIES = 500


@dataclass
class HistoryEntry:
    text: str
    time: str  # ISO 8601, hora local

    @property
    def when(self) -> datetime:
        return datetime.fromisoformat(self.time)


def format_when(when: datetime, now: datetime | None = None) -> str:
    """'hoy 18:35', 'ayer 09:10', '21/10 18:35' o '21/10/2025 18:35'."""
    now = now or datetime.now()
    days = (now.date() - when.date()).days
    if days == 0:
        return f"hoy {when:%H:%M}"
    if days == 1:
        return f"ayer {when:%H:%M}"
    if when.year == now.year:
        return f"{when:%d/%m %H:%M}"
    return f"{when:%d/%m/%Y %H:%M}"


class History:
    """Lista cronológica (la más vieja primero) y un cursor `pos` a la entrada que se está mostrando."""

    def __init__(self, path: Path | None = None, limit: int = MAX_ENTRIES):
        self.path = path
        self.limit = limit
        self.entries: list[HistoryEntry] = []
        self.pos: int | None = None
        self.persist = True

    @classmethod
    def load(cls, path: Path | None, limit: int = MAX_ENTRIES) -> History:
        history = cls(path, limit)
        if path is not None and path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                history.entries = [HistoryEntry(str(e["text"]), str(e["time"])) for e in data][-limit:]
            except (OSError, ValueError, KeyError, TypeError):
                history.entries = []
        return history

    def save(self) -> None:
        if self.path is None or not self.persist:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps([asdict(e) for e in self.entries], ensure_ascii=False, indent=0),
                           encoding="utf-8")
            tmp.replace(self.path)
        except OSError:
            pass

    def delete_file(self) -> None:
        if self.path is not None:
            self.path.unlink(missing_ok=True)

    def __len__(self) -> int:
        return len(self.entries)

    def add(self, text: str, when: datetime | None = None) -> HistoryEntry | None:
        text = text.strip()
        if not text:
            return None
        stamp = (when or datetime.now()).isoformat(timespec="seconds")
        if self.entries and self.entries[-1].text == text:
            self.entries[-1].time = stamp  # repetir la última búsqueda solo actualiza la hora
        else:
            self.entries.append(HistoryEntry(text, stamp))
            del self.entries[:-self.limit]
        self.pos = len(self.entries) - 1
        self.save()
        return self.entries[-1]

    @property
    def current(self) -> HistoryEntry | None:
        return self.entries[self.pos] if self.pos is not None else None

    def can_back(self) -> bool:
        if not self.entries:
            return False
        return self.pos is None or self.pos > 0

    def can_forward(self) -> bool:
        return self.pos is not None and self.pos < len(self.entries) - 1

    def back(self) -> HistoryEntry | None:
        if not self.can_back():
            return None
        self.pos = len(self.entries) - 1 if self.pos is None else self.pos - 1
        return self.current

    def forward(self) -> HistoryEntry | None:
        if not self.can_forward():
            return None
        self.pos += 1
        return self.current

    def go(self, index: int) -> HistoryEntry | None:
        if 0 <= index < len(self.entries):
            self.pos = index
            return self.current
        return None

    def clear(self) -> None:
        self.entries.clear()
        self.pos = None
        self.save()
