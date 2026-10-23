"""Flujo completo con la ventana real: captura -> OCR -> diccionario -> UI.

Por defecto no toca el portapapeles. Con YOMITORU_E2E_CLIPBOARD=1 además copia una
imagen al portapapeles de Windows y espera a que la app la detecte sola.
"""

import ctypes
import gc
import io
import os
import random
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
def app(tk_root, tmp_path):
    db = find_db()
    if db is None:
        pytest.skip("Falta data/kanjidic2.sqlite")
    engine = create_engine("windows")
    try:
        engine.check()
    except OcrUnavailableError as e:
        pytest.skip(str(e))
    a = YomitoruApp(tk.Toplevel(tk_root), KanjiDictionary(db), engine, interval_ms=100, use_tray=False,
                    data_dir=tmp_path)
    yield a
    a.executor.shutdown(wait=True)
    a.quit()
    # liberar la ventana acá, en el hilo de Tk: si el recolector la libera más tarde
    # desde el hilo del OCR, Tk se cuelga (las variables de Tk no son thread-safe)
    del a
    gc.collect()


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
    # tamaño al azar: si el portapapeles ya tenía la misma imagen de una corrida anterior,
    # volver a copiarla no contaría como captura nueva (mismo hash)
    size = random.randint(40, 60)
    _copy_image_to_clipboard(render("猫", size=size))
    assert pump(app, lambda: app.window.text_var.get() == "猫"), (app.window.text_var.get(), app.window.status_var.get())
    _copy_image_to_clipboard(render("勉強", size=size))
    assert pump(app, lambda: app.window.text_var.get() == "勉強")
    assert "べん" in labels(app.window.scroll.inner)


def test_history_arrows_and_window(app):
    for text in ("日本", "猫", "勉強"):
        app.search(text)
    w = app.window
    assert w.back_btn.instate(["!disabled"]) and w.fwd_btn.instate(["disabled"])
    w.back_btn.invoke()
    assert w.text_var.get() == "猫" and "2 de 3" in w.status_var.get()
    w.back_btn.invoke()
    assert w.text_var.get() == "日本" and w.back_btn.instate(["disabled"])
    w.fwd_btn.invoke()
    assert w.text_var.get() == "猫"
    # navegar no agrega entradas
    assert [e.text for e in app.history.entries] == ["日本", "猫", "勉強"]

    w.show_history()
    hw = w.history_window
    assert [hw.tree.item(i, "values")[0] for i in hw.tree.get_children()] == ["勉強", "猫", "日本"]
    assert hw.tree.selection() == ("1",)  # resalta la entrada que se está mostrando
    hw.tree.selection_set("0")
    hw.open_selected()
    assert w.text_var.get() == "日本"
    app.clear_history()
    assert hw.tree.get_children() == () and w.back_btn.instate(["disabled"])
    hw.win.destroy()


def test_history_persists_between_sessions(app, tk_root, tmp_path):
    app.search("漢字")
    assert (tmp_path / "history.json").exists()
    again = YomitoruApp(tk.Toplevel(tk_root), app.dictionary, app.engine, use_tray=False, data_dir=tmp_path)
    try:
        assert again.history.entries[-1].text == "漢字"
        again.history_back()
        assert again.window.text_var.get() == "漢字"
    finally:
        again.executor.shutdown(wait=True)
        again.quit()
        del again
        gc.collect()


def test_options_menu_toggles(app, tmp_path):
    w = app.window
    menu = w.options_menu
    labels = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1)
              if menu.type(i) == "checkbutton"]
    assert "Modo oscuro" in labels and "Siempre visible" in labels and "Vigilar portapapeles" in labels

    app.set_option("dark_mode", False)
    app.search("日")
    light_bg = w.scroll.inner.winfo_children()[0].cget("bg")
    app.set_option("dark_mode", True)
    assert w.option_vars["dark_mode"].get() is True
    dark_bg = w.scroll.inner.winfo_children()[0].cget("bg")
    assert light_bg != dark_bg  # las tarjetas se redibujan con el tema nuevo

    assert "day, sun, Japan, counter for days" in labels_of(w)
    app.set_option("show_english", False)
    assert "day, sun, Japan, counter for days" not in labels_of(w)

    app.set_option("always_on_top", True)
    assert bool(app.root.attributes("-topmost"))

    app.set_option("save_history", False)
    assert not (tmp_path / "history.json").exists()
    app.search("猫")
    assert not (tmp_path / "history.json").exists() and app.history.entries[-1].text == "猫"

    app.set_option("watch_clipboard", False)
    assert not app.watching and "pausa" in w.status_var.get()
    saved = __import__("json").loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert saved["dark_mode"] and saved["always_on_top"] and not saved["watch_clipboard"]


def labels_of(window):
    return labels(window.scroll.inner)
