import re
from datetime import datetime

import pytest

from yomitoru.i18n import DEFAULT_LANGUAGE, LANGUAGES, STRINGS, Translator, system_language

PLACEHOLDER = re.compile(r"\{(\w+)\}")


def test_languages_and_strings_match():
    assert set(LANGUAGES) == set(STRINGS)


@pytest.mark.parametrize("code", list(LANGUAGES))
def test_no_missing_or_extra_keys(code):
    reference = set(STRINGS[DEFAULT_LANGUAGE])
    assert set(STRINGS[code]) == reference, (reference - set(STRINGS[code]), set(STRINGS[code]) - reference)


@pytest.mark.parametrize("code", list(LANGUAGES))
def test_same_placeholders_as_english(code):
    for key, text in STRINGS[code].items():
        expected = set(PLACEHOLDER.findall(STRINGS[DEFAULT_LANGUAGE][key]))
        assert set(PLACEHOLDER.findall(text)) == expected, key


@pytest.mark.parametrize("code", list(LANGUAGES))
def test_dates(code):
    t = Translator(code)
    now = datetime(2026, 10, 23, 20, 0)
    assert "18:35" in t.format_when(datetime(2026, 10, 23, 18, 35), now)
    assert "09:05" in t.format_when(datetime(2026, 10, 22, 9, 5), now)
    assert "09:05" in t.format_when(datetime(2026, 3, 1, 9, 5), now)
    assert "2025" in t.format_when(datetime(2025, 3, 1, 9, 5), now)


def test_spanish_examples():
    t = Translator("es")
    now = datetime(2026, 10, 23, 20, 0)
    assert t.format_when(datetime(2026, 10, 23, 19, 42), now) == "hoy 19:42"
    assert t("captured_at", when=t.format_when(datetime(2026, 10, 23, 19, 42), now)) == "Capturado: hoy 19:42"
    assert t.format_when(datetime(2026, 10, 22, 9, 5), now) == "ayer 09:05"
    assert t.format_when(datetime(2026, 3, 1, 9, 5), now) == "01/03 09:05"


def test_fallbacks():
    assert Translator("xx").lang == DEFAULT_LANGUAGE
    assert Translator("es")("missing_key") == "missing_key"
    assert system_language() in LANGUAGES
