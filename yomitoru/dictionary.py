"""KANJIDIC2: XML parsing, SQLite database building and lookups.

KANJIDIC2 © Electronic Dictionary Research and Development Group (EDRDG),
licence CC BY-SA 4.0 — https://www.edrdg.org/edrdg/licence.html
"""

from __future__ import annotations

import json
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Iterable, Iterator

from .kana import katakana_to_hiragana

# meaning languages in KANJIDIC2; English is used when the requested one is missing
MEANING_LANGS = ("en", "es", "fr", "pt")
SCHEMA_VERSION = "2"


class OutdatedDictionaryError(RuntimeError):
    """The database was built by an older version of the app and must be rebuilt."""


@dataclass
class KanjiInfo:
    literal: str
    onyomi: list[str] = field(default_factory=list)  # already converted to hiragana
    kunyomi: list[str] = field(default_factory=list)
    meanings: dict[str, list[str]] = field(default_factory=dict)  # language -> meanings
    strokes: int | None = None
    grade: int | None = None
    jlpt: int | None = None
    freq: int | None = None

    def meanings_for(self, lang: str) -> tuple[str, list[str]]:
        """(language, meanings) in `lang` if KANJIDIC2 has them; otherwise in English."""
        if self.meanings.get(lang):
            return lang, self.meanings[lang]
        return "en", self.meanings.get("en", [])


def _int(text: str | None) -> int | None:
    try:
        return int(text) if text is not None else None
    except ValueError:
        return None


def parse_character(elem: ET.Element) -> KanjiInfo:
    info = KanjiInfo(literal=elem.findtext("literal", ""))
    misc = elem.find("misc")
    if misc is not None:
        info.strokes = _int(misc.findtext("stroke_count"))
        info.grade = _int(misc.findtext("grade"))
        info.jlpt = _int(misc.findtext("jlpt"))
        info.freq = _int(misc.findtext("freq"))
    for rm in elem.iterfind("reading_meaning/rmgroup"):
        for reading in rm.iterfind("reading"):
            r_type, text = reading.get("r_type"), reading.text or ""
            if r_type == "ja_on":
                info.onyomi.append(katakana_to_hiragana(text))
            elif r_type == "ja_kun":
                info.kunyomi.append(text)
        for meaning in rm.iterfind("meaning"):
            lang = meaning.get("m_lang", "en")
            if lang in MEANING_LANGS:
                info.meanings.setdefault(lang, []).append(meaning.text or "")
    return info


def parse_kanjidic(source: str | Path | IO[bytes]) -> tuple[dict[str, str], Iterator[KanjiInfo]]:
    """Return (header metadata, KanjiInfo iterator). Uses iterparse to avoid loading everything."""
    header: dict[str, str] = {}

    def entries() -> Iterator[KanjiInfo]:
        for _, elem in ET.iterparse(source, events=("end",)):
            if elem.tag == "header":
                header.update({child.tag: child.text or "" for child in elem})
            elif elem.tag == "character":
                yield parse_character(elem)
                elem.clear()

    return header, entries()


SCHEMA = """
CREATE TABLE kanji (
    literal TEXT PRIMARY KEY,
    onyomi TEXT, kunyomi TEXT, meanings TEXT,
    strokes INTEGER, grade INTEGER, jlpt INTEGER, freq INTEGER
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
"""


def build_db(entries: Iterable[KanjiInfo], db_path: Path, header: dict[str, str] | None = None) -> int:
    """Write the SQLite database (replacing it). Returns the number of kanji."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = db_path.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    dump = lambda xs: json.dumps(xs, ensure_ascii=False)  # noqa: E731
    with sqlite3.connect(tmp) as con:
        con.executescript(SCHEMA)
        count = 0
        for k in entries:
            con.execute(
                "INSERT OR REPLACE INTO kanji VALUES (?,?,?,?,?,?,?,?)",
                (k.literal, dump(k.onyomi), dump(k.kunyomi), dump(k.meanings),
                 k.strokes, k.grade, k.jlpt, k.freq),
            )
            count += 1
        # the header is filled in during iteration, so it is saved at the end
        meta = {**(header or {}), "yomitoru_schema": SCHEMA_VERSION}
        con.executemany("INSERT INTO meta VALUES (?,?)", list(meta.items()))
    con.close()
    tmp.replace(db_path)
    return count


class KanjiDictionary:
    def __init__(self, db_path: Path):
        # check_same_thread=False: read-only, queried from both the UI and OCR threads
        self._con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
        if self.meta().get("yomitoru_schema") != SCHEMA_VERSION:
            self._con.close()
            raise OutdatedDictionaryError(str(db_path))

    def lookup(self, literal: str) -> KanjiInfo | None:
        row = self._con.execute("SELECT * FROM kanji WHERE literal = ?", (literal,)).fetchone()
        if row is None:
            return None
        lit, on, kun, meanings, strokes, grade, jlpt, freq = row
        return KanjiInfo(lit, json.loads(on), json.loads(kun), json.loads(meanings), strokes, grade, jlpt, freq)

    def meta(self) -> dict[str, str]:
        try:
            return dict(self._con.execute("SELECT key, value FROM meta").fetchall())
        except sqlite3.DatabaseError:
            return {}

    def __len__(self) -> int:
        return self._con.execute("SELECT COUNT(*) FROM kanji").fetchone()[0]

    def close(self) -> None:
        self._con.close()
