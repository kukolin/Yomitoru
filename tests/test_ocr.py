"""OCR con imágenes generadas con Pillow (se saltea si el OCR japonés de Windows no está)."""

import threading
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from yomitoru.ocr import OcrUnavailableError, create_engine
from yomitoru.ocr.windows_ocr import _untile, choose, clean_text, line_metrics, normalize, variants

FONTS = [Path(r"C:\Windows\Fonts") / n for n in ("YuGothM.ttc", "meiryo.ttc", "msgothic.ttc")]


def render(text: str, size: int = 48, fg="black", bg="white") -> Image.Image:
    font_path = next((f for f in FONTS if f.exists()), None)
    if font_path is None:
        pytest.skip("No hay fuente japonesa instalada")
    font = ImageFont.truetype(str(font_path), size)
    left, top, right, bottom = font.getbbox(text)
    img = Image.new("RGB", (right - left + size, bottom - top + size), bg)
    ImageDraw.Draw(img).text((size // 2 - left, size // 2 - top), text, font=font, fill=fg)
    return img


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("windows")
    try:
        eng.check()
    except OcrUnavailableError as e:
        pytest.skip(str(e))
    return eng


def test_clean_text_removes_spaces_between_japanese():
    assert clean_text("日 本 語 を 勉 強") == "日本語を勉強"
    assert clean_text(" abc def ") == "abc def"


def test_normalize_crops_and_inverts_dark_background():
    img = Image.new("RGB", (200, 100), "#202020")
    ImageDraw.Draw(img).rectangle((50, 30, 89, 69), fill="white")
    out = normalize(img)
    assert out.mode == "L" and out.size == (40, 40)
    assert out.getpixel((20, 20)) < 50  # el "texto" quedó oscuro


def test_line_height_two_lines():
    img = Image.new("L", (100, 100), 255)
    ImageDraw.Draw(img).rectangle((0, 0, 99, 39), fill=0)
    ImageDraw.Draw(img).rectangle((0, 60, 99, 99), fill=0)
    assert line_metrics(img) == (40, 2)


def test_variants_single_char_adds_tiles():
    kinds = [k for k, _, _ in variants(render("猫"))]
    assert "line" in kinds and "tile" in kinds
    assert "tile" not in [k for k, _, _ in variants(render("日本語の勉強"))]


def test_untile_and_choose():
    assert _untile("日日日") == "日"
    assert _untile("一本本本") == "本"
    assert _untile("五ロ一三ロ") == ""
    assert choose(["", "日本語", "五ロ", "日本語", "日本"]) == "日本語"
    assert choose(["", ""]) == ""


@pytest.mark.parametrize("text", ["日本語", "勉強", "猫が好きです"])
def test_recognize_rendered_text(engine, text):
    assert engine.recognize(render(text)) == text


@pytest.mark.parametrize("kanji", ["猫", "本", "日", "水", "語"])
def test_recognize_single_kanji(engine, kanji):
    # 本 y 日 sueltos solo se reconocen gracias a la variante repetida (日日日)
    assert engine.recognize(render(kanji, size=40)) == kanji


def test_recognize_small_capture(engine):
    # captura chica, como un Win+Shift+S de texto de tamaño normal
    assert engine.recognize(render("日本語", size=16)) == "日本語"


def test_recognize_dark_background(engine):
    assert engine.recognize(render("漢字", fg="white", bg="#202020")) == "漢字"


def test_recognize_from_worker_thread(engine):
    result = {}
    t = threading.Thread(target=lambda: result.update(text=engine.recognize(render("日本"))))
    t.start()
    t.join(30)
    assert result.get("text") == "日本"
