import io

import pytest

from yomitoru.dictionary import KanjiDictionary, build_db, parse_kanjidic
from yomitoru.paths import find_db

# Fragmento real (recortado) del formato KANJIDIC2
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<kanjidic2>
<header><file_version>4</file_version><database_version>test</database_version>
<date_of_creation>2026-01-01</date_of_creation></header>
<character>
  <literal>日</literal>
  <misc><grade>1</grade><stroke_count>4</stroke_count><freq>1</freq><jlpt>4</jlpt></misc>
  <reading_meaning><rmgroup>
    <reading r_type="pinyin">ri4</reading>
    <reading r_type="ja_on">ニチ</reading>
    <reading r_type="ja_on">ジツ</reading>
    <reading r_type="ja_kun">ひ</reading>
    <reading r_type="ja_kun">-び</reading>
    <reading r_type="ja_kun">-か</reading>
    <meaning>day</meaning><meaning>sun</meaning>
    <meaning m_lang="fr">jour</meaning>
    <meaning m_lang="es">día</meaning><meaning m_lang="es">sol</meaning>
  </rmgroup><nanori>あ</nanori></reading_meaning>
</character>
<character>
  <literal>丂</literal>
  <misc><stroke_count>2</stroke_count></misc>
  <reading_meaning><rmgroup>
    <reading r_type="ja_on">コウ</reading>
    <meaning>obstruction of breath</meaning>
  </rmgroup></reading_meaning>
</character>
</kanjidic2>
""".encode("utf-8")


def _kun_clean(readings):
    return {r.lstrip("-") for r in readings}


def test_parse_sample():
    header, entries = parse_kanjidic(io.BytesIO(SAMPLE_XML))
    entries = list(entries)
    assert header["database_version"] == "test"
    nichi = entries[0]
    assert nichi.literal == "日"
    assert nichi.onyomi == ["にち", "じつ"]  # katakana -> hiragana
    assert {"ひ", "か"} <= _kun_clean(nichi.kunyomi)
    assert nichi.meanings == ("es", ["día", "sol"])
    assert nichi.meanings_en == ["day", "sun"]
    assert (nichi.strokes, nichi.grade, nichi.jlpt, nichi.freq) == (4, 1, 4, 1)
    # sin significado en español -> cae al inglés
    assert entries[1].meanings == ("en", ["obstruction of breath"])


def test_build_and_lookup(tmp_path):
    header, entries = parse_kanjidic(io.BytesIO(SAMPLE_XML))
    db = tmp_path / "k.sqlite"
    assert build_db(entries, db, header) == 2
    d = KanjiDictionary(db)
    try:
        assert len(d) == 2
        assert d.lookup("日").onyomi == ["にち", "じつ"]
        assert d.lookup("猫") is None
        assert d.meta()["database_version"] == "test"
    finally:
        d.close()


@pytest.fixture(scope="module")
def real_dict():
    path = find_db()
    if path is None:
        pytest.skip("Falta data/kanjidic2.sqlite (correr python -m yomitoru.setup_dict)")
    d = KanjiDictionary(path)
    yield d
    d.close()


@pytest.mark.parametrize("literal, on, kun, meaning", [
    ("日", {"にち", "じつ"}, {"ひ", "か"}, "day"),
    ("本", {"ほん"}, {"もと"}, "book"),
    ("猫", {"びょう"}, {"ねこ"}, "cat"),
    ("水", {"すい"}, {"みず"}, "water"),
])
def test_real_dictionary(real_dict, literal, on, kun, meaning):
    info = real_dict.lookup(literal)
    assert info is not None
    assert on <= set(info.onyomi)
    assert kun <= _kun_clean(info.kunyomi)
    assert meaning in info.meanings_en
    assert len(real_dict) > 13000
