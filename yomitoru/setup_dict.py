"""Descarga KANJIDIC2 una sola vez y lo convierte a data/kanjidic2.sqlite.

Uso:  python -m yomitoru.setup_dict [--force] [--xml ruta/a/kanjidic2.xml.gz]
"""

from __future__ import annotations

import argparse
import gzip
import sys
import urllib.request
from pathlib import Path

from .dictionary import build_db, parse_kanjidic
from .paths import DB_NAME, data_dir

URL = "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"


def download(dest: Path) -> None:
    print(f"Descargando {URL} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(URL, timeout=60) as resp, open(tmp, "wb") as out:
        while chunk := resp.read(1 << 16):
            out.write(chunk)
    tmp.replace(dest)
    print(f"  {dest.stat().st_size / 1e6:.1f} MB")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="volver a descargar y regenerar")
    parser.add_argument("--xml", type=Path, help="usar un kanjidic2.xml.gz ya descargado")
    args = parser.parse_args(argv)

    db_path = data_dir() / DB_NAME
    if db_path.exists() and not args.force:
        print(f"La base ya existe: {db_path} (usá --force para regenerarla)")
        return 0

    gz_path = args.xml or data_dir() / "kanjidic2.xml.gz"
    if args.force or not gz_path.exists():
        if args.xml:
            print(f"No existe {gz_path}", file=sys.stderr)
            return 1
        download(gz_path)

    print("Convirtiendo a SQLite ...")
    with gzip.open(gz_path, "rb") as f:
        header, entries = parse_kanjidic(f)
        count = build_db(entries, db_path, header)
    print(f"Listo: {count} kanji en {db_path} ({db_path.stat().st_size / 1e6:.1f} MB)")
    print("KANJIDIC2 © EDRDG, licencia CC BY-SA 4.0 (https://www.edrdg.org/edrdg/licence.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
