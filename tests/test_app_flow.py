"""Flujo completo con la ventana real: captura -> OCR -> diccionario -> UI.

Por defecto no toca el portapapeles. Con YOMITORU_E2E_CLIPBOARD=1 además copia una
imagen al portapapeles de Windows y espera a que la app la detecte sola.
"""

import ctypes
import io
import os
import time
import tkinter as tk

import pytest

from yomitoru.app import YomitoruApp
from yomitoru.dictionary import KanjiDictionary
from yomitoru.ocr import OcrUnavailableError, create_engine
from yomitoru.paths import find_db

from .test_ocr import render


@pytest.fixture(scope="module")
def tk_root():
    # un solo Tk por proceso: crear y destruir varios falla de forma intermitente en Windows
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def app(tk_root):
    db = find_db()
    if db is None:
        pytest.skip("Falta data/kanjidic2.sqlite")
    engine = create_engine("windows")
    try:
        engine.check()
    except OcrUnavailableError as e:
        pytest.skip(str(e))
    a = YomitoruApp(tk.Toplevel(tk_root), KanjiDictionary(db), engine, interval_ms=100, use_tray=False)
    yield a
    a.executor.shutdown(wait=True)
    a.quit()


def pump(app, until, timeout=10.0):
    end = time.time() + timeout
    while time.time() < end:
        app.root.update()
        if until():
            return True
        time.sleep(0.02)
    return False


def labels(widget):
    out = []
    for child in widget.winfo_children():
        try:
            out.append(child.cget("text"))
        except tk.TclError:
            pass
        out.extend(labels(child))
    return out


def test_capture_to_kanji_cards(app):
    assert pump(app, lambda: app.ocr_ready)
    app.on_capture(render("日本語"))
    assert pump(app, lambda: app.window.text_var.get() == "日本語")
    texts = labels(app.window.scroll.inner)
    for k in "日本語":
        assert k in texts
    assert "にち、じつ" in texts  # on'yomi de 日 en hiragana
    assert any("日本語 en jisho.org" in t for t in labels(app.window.word_row))
    assert "3 kanji" in app.window.status_var.get()


def test_manual_correction(app):
    app.window.set_text("猫")
    app.window._search()
    texts = labels(app.window.scroll.inner)
    assert "猫" in texts and "びょう" in texts and "ねこ" in texts
    assert labels(app.window.word_row) == []  # un solo carácter: sin link de palabra


def _copy_image_to_clipboard(image):
    buf = io.BytesIO()
    image.convert("RGB").save(buf, "BMP")
    dib = buf.getvalue()[14:]  # sin el BITMAPFILEHEADER
    k32, u32 = ctypes.windll.kernel32, ctypes.windll.user32
    k32.GlobalAlloc.restype = ctypes.c_void_p
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [ctypes.c_void_p]
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    u32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    handle = k32.GlobalAlloc(0x0002, len(dib))  # GMEM_MOVEABLE
    ctypes.memmove(k32.GlobalLock(handle), dib, len(dib))
    k32.GlobalUnlock(handle)
    assert u32.OpenClipboard(None)
    u32.EmptyClipboard()
    u32.SetClipboardData(8, handle)  # CF_DIB
    u32.CloseClipboard()


@pytest.mark.skipif(os.environ.get("YOMITORU_E2E_CLIPBOARD") != "1",
                    reason="modifica el portapapeles; activar con YOMITORU_E2E_CLIPBOARD=1")
def test_real_clipboard(app):
    assert pump(app, lambda: app.ocr_ready)
    # otra imagen primero: si el portapapeles ya tenía 勉強 de una corrida anterior,
    # volver a copiarla no cuenta como captura nueva (mismo hash)
    _copy_image_to_clipboard(render("猫"))
    assert pump(app, lambda: app.window.text_var.get() == "猫")
    _copy_image_to_clipboard(render("勉強"))
    assert pump(app, lambda: app.window.text_var.get() == "勉強")
    assert "べん" in labels(app.window.scroll.inner)
