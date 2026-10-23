"""Utilidades de kana y detección de kanji."""

# ァ (U+30A1) .. ヶ (U+30F6) están exactamente 0x60 por encima de ぁ .. ゖ
_KATA_START, _KATA_END = 0x30A1, 0x30F6
_KATA_TO_HIRA = {c: c - 0x60 for c in range(_KATA_START, _KATA_END + 1)}
_KATA_TO_HIRA[0x30FD] = 0x309D  # ヽ -> ゝ
_KATA_TO_HIRA[0x30FE] = 0x309E  # ヾ -> ゞ

# ヷヸヹヺ no tienen hiragana precompuesto: se dejan como están.

_KANJI_RANGES = (
    (0x3400, 0x4DBF),    # Extensión A
    (0x4E00, 0x9FFF),    # Ideogramas unificados CJK
    (0xF900, 0xFAFF),    # Compatibilidad
    (0x20000, 0x2EBEF),  # Extensiones B-F
    (0x30000, 0x3134F),  # Extensión G
)


def katakana_to_hiragana(text: str) -> str:
    """Convierte katakana a hiragana; el resto (ー, puntos, guiones, latín) queda igual."""
    return text.translate(_KATA_TO_HIRA)


def is_kanji(char: str) -> bool:
    code = ord(char)
    return any(lo <= code <= hi for lo, hi in _KANJI_RANGES)


def extract_kanji(text: str) -> list[str]:
    """Kanji del texto, en orden y sin repetir (ignora kana, signos y espacios)."""
    seen: dict[str, None] = {}
    for char in text:
        if is_kanji(char):
            seen.setdefault(char, None)
    return list(seen)
