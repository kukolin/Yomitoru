from yomitoru.kana import extract_kanji, has_japanese, is_kanji, katakana_to_hiragana


def test_katakana_to_hiragana_basic():
    assert katakana_to_hiragana("ニチ") == "にち"
    assert katakana_to_hiragana("ジツ") == "じつ"
    assert katakana_to_hiragana("キョウ") == "きょう"
    assert katakana_to_hiragana("ヴ") == "ゔ"
    assert katakana_to_hiragana("ヶ") == "ゖ"


def test_katakana_to_hiragana_keeps_other_chars():
    # ー, dashes, okurigana dots, hiragana and Latin letters are unchanged
    assert katakana_to_hiragana("コーヒー") == "こーひー"
    assert katakana_to_hiragana("-び") == "-び"
    assert katakana_to_hiragana("ひ.く") == "ひ.く"
    assert katakana_to_hiragana("abc 日") == "abc 日"


def test_is_kanji():
    assert is_kanji("日") and is_kanji("猫") and is_kanji("𠮟")
    assert not is_kanji("ひ") and not is_kanji("カ") and not is_kanji("。") and not is_kanji("a")


def test_extract_kanji_ignores_kana_and_dedupes():
    assert extract_kanji("日本語を勉強します。日本!") == ["日", "本", "語", "勉", "強"]
    assert extract_kanji("ひらがな カタカナ") == []


def test_has_japanese():
    assert has_japanese("日本") and has_japanese("ありがとう") and has_japanese("コーヒー") and has_japanese("ｶﾀｶﾅ")
    assert not has_japanese("Escuchando") and not has_japanese("123 abc") and not has_japanese("")
    assert not has_japanese("・ー")  # Japanese punctuation alone is not text
