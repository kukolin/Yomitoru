import json
from datetime import datetime

from yomitoru.history import CAPTURE, SEARCH, History
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
    assert h.back() is None  # already at the first one
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
    assert again.pos is None and again.back().text == "猫"  # ◀ goes to the latest


def test_corrupt_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{not json", encoding="utf-8")
    assert len(History.load(path)) == 0


def test_source_is_saved(tmp_path):
    path = tmp_path / "history.json"
    h = History.load(path)
    h.add("猫", T0)  # default: screenshot
    h.add("日本", T0, source=SEARCH)
    again = History.load(path)
    assert [e.source for e in again.entries] == [CAPTURE, SEARCH]
    # 0.2.0 histories (no "source") are read as screenshots
    path.write_text('[{"text": "猫", "time": "2026-10-23T18:35:00"}]', encoding="utf-8")
    assert History.load(path).entries[0].source == CAPTURE


def test_settings_roundtrip(tmp_path):
    path = tmp_path / "settings.json"
    s = Settings.load(path)  # first run: defaults
    assert s.watch_clipboard and s.bring_to_front and not s.always_on_top and not s.open_jisho
    assert s.language == "en"  # English by default, whatever the Windows language
    s.dark_mode = True
    s.language = "ja"
    s.save(path)
    loaded = Settings.load(path)
    assert loaded.dark_mode and loaded.language == "ja"


def test_settings_from_older_version_and_corrupt(tmp_path):
    path = tmp_path / "settings.json"
    # 0.2.0 had show_english and save_history, and no language
    path.write_text(json.dumps({"dark_mode": True, "show_english": False, "save_history": False}),
                    encoding="utf-8")
    loaded = Settings.load(path)
    assert loaded.dark_mode is True and not hasattr(loaded, "show_english")
    path.write_text(json.dumps({"language": "xx", "always_on_top": "yes"}), encoding="utf-8")
    loaded = Settings.load(path)
    assert loaded.language != "xx" and loaded.always_on_top is False  # invalid values ignored
    path.write_text("roto", encoding="utf-8")
    assert Settings.load(path).watch_clipboard is True


def test_every_toggle_is_a_bool_setting():
    defaults = Settings()
    assert all(isinstance(getattr(defaults, name), bool) for name in Settings.TOGGLES)
