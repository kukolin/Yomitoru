"""Full flow with the real window: screenshot -> OCR -> dictionary -> UI.

By default the clipboard is not touched. With YOMITORU_E2E_CLIPBOARD=1 an image is also
copied to the Windows clipboard and the test waits for the app to pick it up by itself.

The UI runs in Spanish here (the fixture sets it), so expected texts are Spanish.
"""

import ctypes
import gc
import io
import json
import os
import random
import time
import tkinter as tk

import pytest

from yomitoru.app import YomitoruApp
from yomitoru.dictionary import KanjiDictionary
from yomitoru.i18n import LANGUAGES, STRINGS
from yomitoru.ocr import OcrUnavailableError, create_engine
from yomitoru.paths import find_db

from .test_ocr import render


@pytest.fixture(scope="module")
def tk_root():
    # a single Tk per process: creating and destroying several fails intermittently on Windows
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
    (tmp_path / "settings.json").write_text(json.dumps({"language": "es", "dark_mode": False}), encoding="utf-8")
    a = YomitoruApp(tk.Toplevel(tk_root), KanjiDictionary(db), engine, interval_ms=100, use_tray=False,
                    data_dir=tmp_path)
    yield a
    a.executor.shutdown(wait=True)
    a.quit()
    # free the window here, on the Tk thread: if the garbage collector frees it later
    # from the OCR thread, Tk hangs (Tk variables are not thread-safe)
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


def click(app, widget):
    app.root.deiconify()
    app.root.update()  # simulated clicks only reach widgets already drawn
    widget.event_generate("<Button-1>", x=2, y=2)
    app.root.update()


def labels(widget):
    """Texts shown inside a widget: labels and the read-only, selectable text fields."""
    out = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Text):
            out.append(child.get("1.0", "end-1c"))
            continue
        try:
            out.append(child.cget("text"))
        except tk.TclError:
            pass
        out.extend(labels(child))
    return out


def texts_of(app):
    return [w for w in all_widgets(app.window.scroll.inner) if isinstance(w, tk.Text)]


def all_widgets(widget):
    for child in widget.winfo_children():
        yield child
        yield from all_widgets(child)


def test_capture_to_kanji_cards(app):
    assert pump(app, lambda: app.ocr_ready)
    app.on_capture(render("日本語"))
    assert pump(app, lambda: app.window.text_var.get() == "日本語")
    texts = labels(app.window.scroll.inner)
    for k in "日本語":
        assert k in texts
    assert "にち、じつ" in texts  # on'yomi of 日 in hiragana
    assert "día, solar, Japón, sol, rayo de sol" in texts
    assert "day, sun, Japan, counter for days" not in texts  # the extra English line is no longer shown
    assert labels(app.window.links_row) == ["Buscar en jisho.org"]
    assert app.window.status_var.get().startswith("Capturado: hoy ")


def test_manual_correction_and_jisho_link(app, monkeypatch):
    app.window.set_text("猫")
    app.window._search()
    texts = labels(app.window.scroll.inner)
    assert "猫" in texts and "びょう" in texts and "ねこ" in texts
    assert app.window.status_var.get().startswith("Buscado: hoy ")
    assert app.history.entries[-1].source == "search"

    opened = []
    monkeypatch.setattr("webbrowser.open", opened.append)
    app.window.set_text(" 勉 強 ")  # the link uses what is typed now, even if it was not searched
    click(app, app.window.links_row.winfo_children()[0])
    assert opened == ["https://jisho.org/search/%E5%8B%89%E5%BC%B7"]


def test_listening_toggle(app, tmp_path):
    toggle = app.window.listening
    assert toggle.label.cget("text") == "Escuchando" and app.watching
    click(app, toggle.label)
    assert not app.watching and toggle.label.cget("text") == "Apagado"
    assert app.window.status_var.get() == "Apagado: las capturas no se procesan."
    assert json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))["watch_clipboard"] is False
    click(app, toggle.dot)
    assert app.watching and toggle.label.cget("text") == "Escuchando"


def _copy_image_to_clipboard(image):
    buf = io.BytesIO()
    image.convert("RGB").save(buf, "BMP")
    dib = buf.getvalue()[14:]  # without the BITMAPFILEHEADER
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
                    reason="overwrites the clipboard; enable with YOMITORU_E2E_CLIPBOARD=1")
def test_real_clipboard(app):
    assert pump(app, lambda: app.ocr_ready)
    # random size: if the clipboard still holds the same image from a previous run,
    # copying it again would not count as a new screenshot (same hash)
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
    assert w.text_var.get() == "猫" and w.status_var.get().startswith("Buscado: hoy ")
    assert "de 3" not in w.status_var.get()  # «Historial: 2 de 3» is no longer shown
    w.back_btn.invoke()
    assert w.text_var.get() == "日本" and w.back_btn.instate(["disabled"])
    w.fwd_btn.invoke()
    assert w.text_var.get() == "猫"
    # navigating does not add entries
    assert [e.text for e in app.history.entries] == ["日本", "猫", "勉強"]

    w.show_history()
    hw = w.history_window
    assert [hw.tree.item(i, "values")[0] for i in hw.tree.get_children()] == ["勉強", "猫", "日本"]
    assert hw.tree.selection() == ("1",)  # highlights the entry being shown
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


def menu_labels(menu):
    return [menu.entrycget(i, "label") for i in range(menu.index("end") + 1) if menu.type(i) != "separator"]


def test_options_menu(app, tmp_path):
    w = app.window
    assert menu_labels(w.options_menu) == ["Mostrar la ventana al capturar", "Siempre visible", "Modo oscuro",
                                           "Idioma / Language"]
    assert menu_labels(w.languages_menu) == list(LANGUAGES.values())

    app.search("日")
    light_bg = w.scroll.inner.winfo_children()[0].cget("bg")
    app.set_option("dark_mode", True)
    assert w.option_vars["dark_mode"].get() is True
    assert w.scroll.inner.winfo_children()[0].cget("bg") != light_bg  # tarjetas redibujadas

    app.set_option("always_on_top", True)
    assert bool(app.root.attributes("-topmost"))
    saved = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert saved["dark_mode"] and saved["always_on_top"]


def test_change_language_live(app, tmp_path):
    app.window.set_text("日本")
    app.window._search()
    w = app.window
    w.languages_menu.invoke(list(LANGUAGES).index("fr"))  # same as picking it in the menu
    assert app.settings.language == "fr"
    assert json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))["language"] == "fr"
    w = app.window
    assert w.listening.label.cget("text") == "À l'écoute"
    assert labels(w.links_row) == ["Chercher sur jisho.org"]
    assert w.status_var.get().startswith("Recherché : aujourd'hui ")
    texts = labels(w.scroll.inner)
    assert "Sens" in texts and "jour, soleil, Japon, compteur de jours" in texts  # meaning in French
    assert w.text_var.get() == "日本"  # what was being shown is kept

    app.set_option("language", "de")  # German: not in KANJIDIC2, shown in English with a note
    texts = labels(app.window.scroll.inner)
    assert "Bedeutung" in texts and "day, sun, Japan, counter for days" in texts and "(auf Englisch)" in texts

    app.set_option("language", "ja")
    texts = labels(app.window.scroll.inner)
    assert "音読み" in texts and "訓読み" in texts and "4画" in " ".join(texts)
    assert menu_labels(app.window.options_menu)[-1] == "言語 / Language"


def test_every_language_renders(app):
    app.search("日本")
    app.window.show_history()
    app.window.show_about()
    for code in LANGUAGES:
        app.set_option("language", code)
        assert app.window.listening.label.cget("text") == STRINGS[code]["listening"]
        assert labels(app.window.links_row) == [STRINGS[code]["search_jisho"]]
        assert app.window.history_window.win.title().startswith(STRINGS[code]["hist_title"])
    app.window.history_window.win.destroy()


def test_no_kanji_message(app):
    app.search("ありがとう")
    assert labels(app.window.scroll.inner) == ["No hay kanji en el texto."]


def test_secondary_windows_open_over_main_window(app):
    root = app.root
    root.deiconify()
    root.geometry("500x620+300+150")
    root.update()
    main_center = (root.winfo_rootx() + root.winfo_width() // 2, root.winfo_rooty() + root.winfo_height() // 2)
    app.window.show_about()
    app.window.show_history()
    for win in (app.window._about, app.window.history_window.win):
        win.update()
        center = (win.winfo_rootx() + win.winfo_width() // 2, win.winfo_rooty() + win.winfo_height() // 2)
        assert abs(center[0] - main_center[0]) <= 20 and abs(center[1] - main_center[1]) <= 60, (center, main_center)
        win.destroy()


def test_card_text_is_selectable_but_read_only(app):
    app.search("日")
    fields = texts_of(app)
    assert [f.get("1.0", "end-1c") for f in fields][:3] == ["日", "にち、じつ", "ひ、-び、-か"]
    reading = fields[1]
    assert reading.cget("state") == "disabled"  # cannot be edited...
    reading.tag_add("sel", "1.0", "1.2")  # ...but can be selected
    assert reading.get("sel.first", "sel.last") == "にち"


@pytest.mark.skipif(os.environ.get("YOMITORU_E2E_CLIPBOARD") != "1",
                    reason="overwrites the clipboard; enable with YOMITORU_E2E_CLIPBOARD=1")
def test_copy_selection_and_copy_button(app):
    app.search("猫")
    app.root.deiconify()
    app.root.update()
    reading = texts_of(app)[2]  # kun'yomi: ねこ
    reading.tag_add("sel", "1.0", "1.1")
    reading.event_generate("<<Copy>>")  # what Ctrl+C does
    assert app.root.clipboard_get() == "ね"

    status_before = app.window.status_var.get()
    card = texts_of(app)[0].master.master
    button = [w for w in card.winfo_children() if isinstance(w, tk.Label) and getattr(w, "image", None)][0]
    assert button.grid_info()["column"] == 2  # right side of the card
    click(app, button)
    assert app.root.clipboard_get() == "猫"
    assert app.window.status_var.get() == "Copiado: 猫"
    assert pump(app, lambda: app.window.status_var.get() == status_before, timeout=4)
    assert app.watcher.poll() is None  # copying text never triggers a new lookup


def test_mouse_wheel_over_card_text_scrolls_the_list(app):
    app.root.deiconify()
    app.root.geometry("500x400")
    app.search("日本語勉強漢字辞書")
    app.root.update()
    canvas = app.window.scroll.canvas
    before = canvas.yview()
    meaning = texts_of(app)[3]
    meaning.event_generate("<MouseWheel>", delta=-120)
    app.root.update()
    assert canvas.yview() != before  # the list moved...
    assert meaning.yview()[0] == 0.0  # ...and the text inside the card did not
