"""Entry point: ties together clipboard, OCR, dictionary and window."""

from __future__ import annotations

import argparse
import ctypes
import queue
import sys
import tkinter as tk
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import messagebox

from PIL import Image

from . import APP_NAME
from .clipboard import ClipboardWatcher
from .dictionary import KanjiDictionary, OutdatedDictionaryError
from .history import CAPTURE, SEARCH, History, HistoryEntry
from .i18n import Translator
from .kana import has_japanese
from .lookup import jisho_word_url, lookup_text
from .ocr import OcrEngine, OcrUnavailableError, create_engine
from .paths import config_dir, find_db
from .settings import Settings
from .tray import create_tray
from .ui import MainWindow

_DEFAULT = object()


class YomitoruApp:
    def __init__(self, root: tk.Tk | tk.Toplevel, dictionary: KanjiDictionary, engine: OcrEngine,
                 interval_ms: int = 500, use_tray: bool = True, data_dir: Path | None = _DEFAULT):
        self.root = root
        self.dictionary = dictionary
        self.engine = engine
        self.interval_ms = interval_ms
        # settings and history in %APPDATA%\Yomitoru (data_dir=None: save nothing, for tests)
        cfg = config_dir() if data_dir is _DEFAULT else data_dir
        self.settings_path = cfg / "settings.json" if cfg else None
        self.settings = Settings.load(self.settings_path)
        self.history = History.load(cfg / "history.json" if cfg else None)
        self.t = Translator(self.settings.language)
        self.running = True
        self.ocr_ready = False
        self.watcher = ClipboardWatcher()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ocr")
        # Tk is not thread-safe: worker threads (OCR, tray) queue functions for the UI thread to run
        self.calls: queue.Queue = queue.Queue()

        self.window = MainWindow(root, self, on_close=self.on_close, dict_meta=dictionary.meta())
        self._status_idle()
        self.tray = None
        if use_tray:
            self.tray = create_tray(
                translate=lambda key: self.t(key),
                on_show=lambda: self.calls.put(self.window.bring_to_front),
                on_toggle=lambda: self.calls.put(lambda: self.set_watching(not self.watching)),
                is_watching=lambda: self.watching,
                on_about=lambda: self.calls.put(self._show_about),
                on_quit=lambda: self.calls.put(self.quit),
            )

        self.watcher.prime()
        self.executor.submit(self._check_ocr)
        root.after(100, self._drain_calls)
        root.after(self.interval_ms, self._poll_clipboard)

    # --- threads -> UI
    def _drain_calls(self):
        if not self.running:
            return
        try:
            while True:
                self.calls.get_nowait()()
        except queue.Empty:
            pass
        self.root.after(50, self._drain_calls)

    def _check_ocr(self):
        try:
            self.engine.check()
        except OcrUnavailableError as e:
            self.calls.put(lambda: self._ocr_unavailable(e))
        else:
            self.ocr_ready = True

    def _ocr_unavailable(self, error: OcrUnavailableError):
        self.window.set_status("ocr_status_unavailable")
        self.window.bring_to_front()
        message = self.t("ocr_install_help") if error.code == "language_missing" else str(error)
        messagebox.showwarning(self.t("ocr_title", app=APP_NAME), message, parent=self.root)

    def _status_idle(self):
        self.window.set_status("waiting" if self.watching else "paused")

    def _show_about(self):
        self.window.bring_to_front()
        self.window.show_about()

    @property
    def watching(self) -> bool:
        return self.settings.watch_clipboard

    # --- settings
    def set_option(self, name: str, value):
        if name == "watch_clipboard":
            self.set_watching(value)
            return
        setattr(self.settings, name, value)
        self.settings.save(self.settings_path)
        self.window.sync_option(name, value)
        if name == "always_on_top":
            self.window.apply_topmost()
        elif name == "dark_mode":
            self.window.apply_theme()
        elif name == "language":
            self.t = Translator(value)
            self.window.retranslate()
            if self.tray:
                self.tray.refresh()

    # --- clipboard
    def _poll_clipboard(self):
        if not self.running:
            return
        if self.watching:
            image = self.watcher.poll()
            if image is not None:
                self.on_capture(image)
        self.root.after(self.interval_ms, self._poll_clipboard)

    def set_watching(self, watching: bool):
        self.settings.watch_clipboard = watching
        self.settings.save(self.settings_path)
        self.window.update_listening()
        if watching:
            self.watcher.prime()  # ignore whatever was copied while paused
        self._status_idle()
        if self.tray:
            self.tray.refresh()

    @property
    def direct_to_jisho(self) -> bool:
        """«Open jisho.org directly»: Japanese text goes to the browser without showing the window."""
        return self.settings.open_jisho and self.ocr_ready

    def on_capture(self, image: Image.Image):
        self.window.set_capture(image)
        if self.settings.bring_to_front and not self.direct_to_jisho:
            self.window.bring_to_front()
        if not self.ocr_ready:
            self.window.set_status("capture_no_ocr")
            return
        self.window.set_status("recognizing")
        future = self.executor.submit(self.engine.recognize, image)
        future.add_done_callback(lambda f: self.calls.put(lambda: self._ocr_done(f)))

    def _ocr_done(self, future):
        try:
            text = future.result()
        except Exception as e:  # noqa: BLE001 - reported in the window
            self._show_if_direct()
            self.window.set_status("ocr_error", error=e)
            return
        self.window.set_text(text)
        if self.direct_to_jisho and has_japanese(text):
            compact = "".join(text.split())
            webbrowser.open(jisho_word_url(compact))
            self.search(text, source=CAPTURE)  # still saved in the history, window updated in the background
            self.window.set_status("opened_jisho", text=compact)
            return
        self._show_if_direct()  # nothing Japanese recognized: show the app so it can be fixed by hand
        self.search(text, source=CAPTURE)

    def _show_if_direct(self):
        """In «open jisho.org directly» mode the window was not shown on capture; show it now."""
        if self.direct_to_jisho and self.settings.bring_to_front:
            self.window.bring_to_front()

    # --- search
    def search(self, text: str, source: str = SEARCH):
        """Look up the text and add it to the history (`source`: screenshot or typed)."""
        result = lookup_text(text, self.dictionary)
        self.window.show_result(result)
        entry = self.history.add(result.text, source=source) if result.text else None
        if entry is not None:
            self._status_for(entry)
        else:
            self._status_idle()
        self.window.update_nav()

    def _status_for(self, entry: HistoryEntry):
        """«Captured: today 19:42» or «Searched: today 19:42»."""
        self.window.set_status("captured_at" if entry.source == CAPTURE else "searched_at", when=entry.when)

    # --- history
    def history_back(self):
        self._show_history_entry(self.history.back())

    def history_forward(self):
        self._show_history_entry(self.history.forward())

    def open_history(self, index: int):
        self._show_history_entry(self.history.go(index))

    def clear_history(self):
        self.history.clear()
        self.history.delete_file()
        self.window.update_nav()
        self.window.set_status("history_cleared")

    def _show_history_entry(self, entry: HistoryEntry | None):
        if entry is None:
            return
        self.window.set_capture(None)  # screenshots are not stored, only the text
        self.window.set_text(entry.text)
        self.window.show_result(lookup_text(entry.text, self.dictionary))
        self._status_for(entry)
        self.window.update_nav()

    # --- exit
    def on_close(self):
        if self.tray:
            self.window.hide()  # keeps running in the tray
        else:
            self.quit()

    def quit(self):
        self.running = False
        if self.tray:
            self.tray.stop()
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def _enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        pass


def _already_running() -> bool:
    """Named Windows mutex: prevents two instances from watching the same clipboard."""
    try:
        kernel32 = ctypes.windll.kernel32
        _already_running.handle = kernel32.CreateMutexW(None, False, "Local\\Yomitoru-single-instance")
        return kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
    except (AttributeError, OSError):
        return False


def _open_dictionary(t: Translator) -> KanjiDictionary | None:
    """Open the dictionary; offer to download it if missing, rebuild it if it is from an older version."""
    path = find_db()
    if path is not None:
        try:
            return KanjiDictionary(path)
        except OutdatedDictionaryError:
            pass  # rebuilt below without asking (reuses the downloaded XML if present)
    elif not messagebox.askyesno(APP_NAME, t("dict_missing")):
        return None
    from .setup_dict import main as setup_main
    try:
        setup_main([])
        return KanjiDictionary(find_db())
    except Exception as e:  # noqa: BLE001
        messagebox.showerror(APP_NAME, t("dict_failed", error=e))
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="yomitoru", description="Lightweight, fast kanji lookup from screenshots.")
    parser.add_argument("--ocr", default="windows", choices=["windows", "manga"], help="OCR engine")
    parser.add_argument("--interval", type=int, default=500, help="milliseconds between clipboard checks")
    parser.add_argument("--no-tray", action="store_true", help="no system tray icon")
    args = parser.parse_args(argv)

    _enable_dpi_awareness()
    t = Translator(Settings.load(config_dir() / "settings.json").language)
    root = tk.Tk()
    if _already_running():
        root.withdraw()
        messagebox.showinfo(APP_NAME, t("already_running"))
        root.destroy()
        return 0
    dictionary = _open_dictionary(t)
    if dictionary is None:
        root.destroy()
        return 1
    YomitoruApp(root, dictionary, create_engine(args.ocr), interval_ms=args.interval, use_tray=not args.no_tray)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
