"""KANJIDIC2: parseo del XML, construcción de la base SQLite y consultas.

KANJIDIC2 © Electronic Dictionary Research and Development Group (EDRDG),
licencia CC BY-SA 4.0 — https://www.edrdg.org/edrdg/licence.html
"""

from __future__ import annotations

import json
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Iterable, Iterator

from .kana import katakana_to_hiragana


@dataclass
class KanjiInfo:
    literal: str
    onyomi: list[str] = field(default_factory=list)  # ya convertido a hiragana
    kunyomi: list[str] = field(default_factory=list)
    meanings_es: list[str] = field(default_factory=list)
    meanings_en: list[str] = field(default_factory=list)
    strokes: int | None = None
    grade: int | None = None
    jlpt: int | None = None
    freq: int | None = None

    @property
    def meanings(self) -> tuple[str, list[str]]:
        """(idioma, significados): español si existe, si no inglés."""
        if self.meanings_es:
            return "es", self.meanings_es
        return "en", self.meanings_en


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
            if lang == "en":
                info.meanings_en.append(meaning.text or "")
            elif lang == "es":
                info.meanings_es.append(meaning.text or "")
    return info


def parse_kanjidic(source: str | Path | IO[bytes]) -> tuple[dict[str, str], Iterator[KanjiInfo]]:
    """Devuelve (metadatos del header, iterador de KanjiInfo). Usa iterparse para no cargar todo."""
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
    onyomi TEXT, kunyomi TEXT, meanings_es TEXT, meanings_en TEXT,
    strokes INTEGER, grade INTEGER, jlpt INTEGER, freq INTEGER
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
"""


def build_db(entries: Iterable[KanjiInfo], db_path: Path, header: dict[str, str] | None = None) -> int:
    """Escribe la base SQLite (reemplazándola). Devuelve la cantidad de kanji."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = db_path.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    dump = lambda xs: json.dumps(xs, ensure_ascii=False)  # noqa: E731
    with sqlite3.connect(tmp) as con:
        con.executescript(SCHEMA)
        count = 0
        for k in entries:
            con.execute(
                "INSERT OR REPLACE INTO kanji VALUES (?,?,?,?,?,?,?,?,?)",
                (k.literal, dump(k.onyomi), dump(k.kunyomi), dump(k.meanings_es),
                 dump(k.meanings_en), k.strokes, k.grade, k.jlpt, k.freq),
            )
            count += 1
        # header se completa durante la iteración, por eso se guarda al final
        con.executemany("INSERT INTO meta VALUES (?,?)", list((header or {}).items()))
    con.close()
    tmp.replace(db_path)
    return count


class KanjiDictionary:
    def __init__(self, db_path: Path):
        # check_same_thread=False: solo lecturas, se consulta desde el hilo de la UI y del OCR
        self._con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)

    def lookup(self, literal: str) -> KanjiInfo | None:
        row = self._con.execute("SELECT * FROM kanji WHERE literal = ?", (literal,)).fetchone()
        if row is None:
            return None
        lit, on, kun, es, en, strokes, grade, jlpt, freq = row
        return KanjiInfo(lit, json.loads(on), json.loads(kun), json.loads(es), json.loads(en),
                         strokes, grade, jlpt, freq)

    def meta(self) -> dict[str, str]:
        return dict(self._con.execute("SELECT key, value FROM meta").fetchall())

    def __len__(self) -> int:
        return self._con.execute("SELECT COUNT(*) FROM kanji").fetchone()[0]

    def close(self) -> None:
        self._con.close()
