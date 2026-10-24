"""Kana utilities and kanji detection."""

# ァ (U+30A1) .. ヶ (U+30F6) are exactly 0x60 above ぁ .. ゖ
_KATA_START, _KATA_END = 0x30A1, 0x30F6
_KATA_TO_HIRA = {c: c - 0x60 for c in range(_KATA_START, _KATA_END + 1)}
_KATA_TO_HIRA[0x30FD] = 0x309D  # ヽ -> ゝ
_KATA_TO_HIRA[0x30FE] = 0x309E  # ヾ -> ゞ

# ヷヸヹヺ have no precomposed hiragana: they are left as they are.

_KANJI_RANGES = (
    (0x3400, 0x4DBF),    # Extension A
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    (0xF900, 0xFAFF),    # Compatibility
    (0x20000, 0x2EBEF),  # Extensions B-F
    (0x30000, 0x3134F),  # Extension G
)


def katakana_to_hiragana(text: str) -> str:
    """Convert katakana to hiragana; everything else (ー, dots, dashes, Latin) is unchanged."""
    return text.translate(_KATA_TO_HIRA)


def is_kanji(char: str) -> bool:
    code = ord(char)
    return any(lo <= code <= hi for lo, hi in _KANJI_RANGES)


_KANA_RANGES = (
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0x31F0, 0x31FF),  # Katakana phonetic extensions
    (0xFF66, 0xFF9F),  # Half-width katakana
)


def is_kana(char: str) -> bool:
    code = ord(char)
    return any(lo <= code <= hi for lo, hi in _KANA_RANGES)


def has_japanese(text: str) -> bool:
    """True if the text has at least one kanji or kana (punctuation and Latin letters do not count)."""
    return any(is_kanji(c) or (is_kana(c) and c not in "・ー゛゜") for c in text)


def extract_kanji(text: str) -> list[str]:
    """Kanji in the text, in order and without repeats (ignores kana, symbols and spaces)."""
    seen: dict[str, None] = {}
    for char in text:
        if is_kanji(char):
            seen.setdefault(char, None)
    return list(seen)
