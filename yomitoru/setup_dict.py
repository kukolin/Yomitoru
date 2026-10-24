"""Download KANJIDIC2 once and convert it to data/kanjidic2.sqlite.

Usage:  python -m yomitoru.setup_dict [--force] [--xml path/to/kanjidic2.xml.gz]
"""

from __future__ import annotations

import argparse
import gzip
import sqlite3
import sys
import urllib.request
from pathlib import Path

from .dictionary import KanjiDictionary, OutdatedDictionaryError, build_db, parse_kanjidic
from .paths import DB_NAME, data_dir

URL = "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"


def download(dest: Path) -> None:
    print(f"Downloading {URL} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(URL, timeout=60) as resp, open(tmp, "wb") as out:
        while chunk := resp.read(1 << 16):
            out.write(chunk)
    tmp.replace(dest)
    print(f"  {dest.stat().st_size / 1e6:.1f} MB")


def is_current(db_path: Path) -> bool:
    """True if the database exists and has the format of this version of the app."""
    if not db_path.is_file():
        return False
    try:
        KanjiDictionary(db_path).close()
        return True
    except (OutdatedDictionaryError, sqlite3.DatabaseError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="download again and rebuild")
    parser.add_argument("--xml", type=Path, help="use an already downloaded kanjidic2.xml.gz")
    args = parser.parse_args(argv)

    db_path = data_dir() / DB_NAME
    if is_current(db_path) and not args.force:
        print(f"The database already exists: {db_path} (use --force to rebuild it)")
        return 0
    if db_path.exists() and not args.force:
        print("The database is from an older version: rebuilding it.")

    gz_path = args.xml or data_dir() / "kanjidic2.xml.gz"
    if not gz_path.exists() or (args.force and not args.xml):
        if args.xml:
            print(f"Not found: {gz_path}", file=sys.stderr)
            return 1
        download(gz_path)

    print("Converting to SQLite ...")
    with gzip.open(gz_path, "rb") as f:
        header, entries = parse_kanjidic(f)
        count = build_db(entries, db_path, header)
    print(f"Done: {count} kanji in {db_path} ({db_path.stat().st_size / 1e6:.1f} MB)")
    print("KANJIDIC2 © EDRDG, licence CC BY-SA 4.0 (https://www.edrdg.org/edrdg/licence.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
