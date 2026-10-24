"""From recognized text to what the window shows (no UI dependencies)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from .dictionary import KanjiDictionary, KanjiInfo
from .kana import extract_kanji


def jisho_kanji_url(kanji: str) -> str:
    return f"https://jisho.org/search/{quote(kanji)}%23kanji"


def jisho_word_url(text: str) -> str:
    return f"https://jisho.org/search/{quote(text)}"


@dataclass
class KanjiEntry:
    literal: str
    info: KanjiInfo | None  # None if not in KANJIDIC2
    url: str


@dataclass
class LookupResult:
    text: str
    kanji: list[KanjiEntry]
    word_url: str | None  # only when there is more than one character


def lookup_text(text: str, dictionary: KanjiDictionary) -> LookupResult:
    compact = "".join(text.split())
    entries = [KanjiEntry(k, dictionary.lookup(k), jisho_kanji_url(k)) for k in extract_kanji(compact)]
    word_url = jisho_word_url(compact) if len(compact) > 1 else None
    return LookupResult(compact, entries, word_url)
