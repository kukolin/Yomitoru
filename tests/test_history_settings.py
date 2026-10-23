import json
from datetime import datetime

from yomitoru.history import History, format_when
from yomitoru.settings import Settings

T0 = datetime(2026, 10, 23, 18, 35)


def test_add_and_navigate():
    h = History()
    assert not h.can_back() and not h.can_forward()
    for text in ("日本", "猫", "勉強"):
        h.add(text, T0)
    assert h.current.text == "勉強"
    assert h.can_back() and not h.can_forward()
    assert h.back().text == "猫"
    assert h.back().text == "日本"
    assert h.back() is None  # ya está en la primera
    assert h.forward().text == "猫"
    assert h.forward().text == "勉強"
    assert h.forward() is None


def test_new_search_after_going_back_goes_to_end():
    h = History()
    for text in ("a", "b", "c"):
        h.add(text, T0)
    h.back()
    h.back()
    h.add("d", T0)
    assert [e.text for e in h.entries] == ["a", "b", "c", "d"]
    assert h.current.text == "d"


def test_repeated_last_search_is_not_duplicated():
    h = History()
    h.add("猫", T0)
    h.add(" 猫 ", datetime(2026, 10, 23, 19, 0))
    assert len(h) == 1 and h.entries[0].time == "2026-10-23T19:00:00"
    assert h.add("   ") is None


def test_limit_drops_oldest():
    h = History(limit=3)
    for text in "abcde":
        h.add(text, T0)
    assert [e.text for e in h.entries] == ["c", "d", "e"]


def test_go_and_clear():
    h = History()
    for text in "abc":
        h.add(text, T0)
    assert h.go(0).text == "a" and h.go(9) is None
    h.clear()
    assert len(h) == 0 and h.current is None and not h.can_back()


def test_persistence(tmp_path):
    path = tmp_path / "sub" / "history.json"
    h = History.load(path)
    h.add("日本語", T0)
    h.add("猫", T0)
    again = History.load(path)
    assert [e.text for e in again.entries] == ["日本語", "猫"]
    assert again.pos is None and again.back().text == "猫"  # ◀ lleva a la última


def test_persist_off_and_corrupt_file(tmp_path):
    path = tmp_path / "history.json"
    h = History.load(path)
    h.persist = False
    h.add("猫", T0)
    assert not path.exists()
    path.write_text("{no es json", encoding="utf-8")
    assert len(History.load(path)) == 0


def test_format_when():
    now = datetime(2026, 10, 23, 20, 0)
    assert format_when(datetime(2026, 10, 23, 18, 35), now) == "hoy 18:35"
    assert format_when(datetime(2026, 10, 22, 9, 5), now) == "ayer 09:05"
    assert format_when(datetime(2026, 3, 1, 9, 5), now) == "01/03 09:05"
    assert format_when(datetime(2025, 3, 1, 9, 5), now) == "01/03/2025 09:05"


def test_settings_roundtrip(tmp_path):
    path = tmp_path / "settings.json"
    s = Settings.load(path)  # primera vez: valores por defecto
    assert s.watch_clipboard and s.save_history and not s.always_on_top
    s.dark_mode = True
    s.always_on_top = True
    s.save(path)
    loaded = Settings.load(path)
    assert loaded.dark_mode and loaded.always_on_top


def test_settings_ignores_unknown_and_corrupt(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"dark_mode": True, "otra_cosa": 1}), encoding="utf-8")
    assert Settings.load(path).dark_mode is True
    path.write_text("roto", encoding="utf-8")
    assert Settings.load(path).watch_clipboard is True


def test_every_setting_has_a_label():
    from dataclasses import fields
    assert {f.name for f in fields(Settings)} == set(Settings.LABELS)
