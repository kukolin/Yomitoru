"""Punto de entrada: une portapapeles, OCR, diccionario y ventana."""

from __future__ import annotations

import argparse
import ctypes
import queue
import sys
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox

from pathlib import Path

from PIL import Image

from . import APP_NAME
from .clipboard import ClipboardWatcher
from .dictionary import KanjiDictionary
from .history import History, HistoryEntry, format_when
from .lookup import lookup_text
from .ocr import OcrEngine, OcrUnavailableError, create_engine
from .paths import config_dir, find_db
from .settings import Settings
from .tray import create_tray
from .ui import WAITING, MainWindow

_DEFAULT = object()


class YomitoruApp:
    def __init__(self, root: tk.Tk | tk.Toplevel, dictionary: KanjiDictionary, engine: OcrEngine,
                 interval_ms: int = 500, use_tray: bool = True, data_dir: Path | None = _DEFAULT):
        self.root = root
        self.dictionary = dictionary
        self.engine = engine
        self.interval_ms = interval_ms
        # opciones e historial en %APPDATA%\Yomitoru (data_dir=None: no guardar nada, para tests)
        cfg = config_dir() if data_dir is _DEFAULT else data_dir
        self.settings_path = cfg / "settings.json" if cfg else None
        self.settings = Settings.load(self.settings_path)
        self.history = History.load(cfg / "history.json" if cfg else None)
        self.history.persist = self.settings.save_history
        self.running = True
        self.ocr_ready = False
        self.watcher = ClipboardWatcher()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ocr")
        # Tk no es thread-safe: los hilos (OCR, bandeja) encolan funciones que corre el hilo de la UI
        self.calls: queue.Queue = queue.Queue()

        self.window = MainWindow(root, self, on_close=self.on_close, dict_meta=dictionary.meta())
        if not self.watching:
            self.window.set_status("Vigilancia en pausa (se activa en Opciones).")
        self.tray = None
        if use_tray:
            self.tray = create_tray(
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

    # --- hilos -> UI
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
            self.calls.put(lambda: self._ocr_unavailable(str(e)))
        else:
            self.ocr_ready = True

    def _ocr_unavailable(self, message: str):
        self.window.set_status("OCR no disponible: podés escribir el texto a mano y presionar Buscar.")
        self.window.bring_to_front()
        messagebox.showwarning(f"{APP_NAME}: OCR no disponible", message, parent=self.root)

    def _show_about(self):
        self.window.bring_to_front()
        self.window.show_about()

    @property
    def watching(self) -> bool:
        return self.settings.watch_clipboard

    # --- opciones
    def set_option(self, name: str, value: bool):
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
        elif name == "show_english":
            self.window.rerender()
        elif name == "save_history":
            self.history.persist = value
            if value:
                self.history.save()
            else:
                self.history.delete_file()

    # --- portapapeles
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
        self.window.sync_option("watch_clipboard", watching)
        if watching:
            self.watcher.prime()  # no procesar lo copiado mientras estaba en pausa
        self.window.set_status(WAITING if watching else "Vigilancia en pausa.")
        if self.tray:
            self.tray.refresh()

    def on_capture(self, image: Image.Image):
        self.window.set_capture(image)
        if self.settings.bring_to_front:
            self.window.bring_to_front()
        if not self.ocr_ready:
            self.window.set_status("Captura recibida, pero el OCR no está disponible.")
            return
        self.window.set_status("Reconociendo…")
        future = self.executor.submit(self.engine.recognize, image)
        future.add_done_callback(lambda f: self.calls.put(lambda: self._ocr_done(f)))

    def _ocr_done(self, future):
        try:
            text = future.result()
        except Exception as e:  # noqa: BLE001 - se informa en la ventana
            self.window.set_status(f"Error de OCR: {e}")
            return
        self.window.set_text(text)
        self.search(text)

    # --- búsqueda
    def search(self, text: str):
        result = lookup_text(text, self.dictionary)
        self.window.show_result(result)
        n = len(result.kanji)
        self.window.set_status(f"{n} kanji encontrado{'s' if n != 1 else ''}." if result.text
                               else "No se reconoció texto.")
        if result.text:
            self.history.add(result.text)
        self.window.update_nav()

    # --- historial
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
        self.window.set_status("Historial borrado.")

    def _show_history_entry(self, entry: HistoryEntry | None):
        if entry is None:
            return
        self.window.set_capture(None)  # las capturas no se guardan, solo el texto
        self.window.set_text(entry.text)
        self.window.show_result(lookup_text(entry.text, self.dictionary))
        self.window.set_status(f"Historial: {self.history.pos + 1} de {len(self.history)} · "
                               f"{format_when(entry.when)}")
        self.window.update_nav()

    # --- salida
    def on_close(self):
        if self.tray:
            self.window.hide()  # sigue en la bandeja
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
    """Mutex con nombre de Windows: evita dos instancias vigilando el mismo portapapeles."""
    try:
        kernel32 = ctypes.windll.kernel32
        _already_running.handle = kernel32.CreateMutexW(None, False, "Local\\Yomitoru-single-instance")
        return kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
    except (AttributeError, OSError):
        return False


def _ensure_dictionary(root: tk.Tk):
    path = find_db()
    if path is not None:
        return path
    if not messagebox.askyesno(
        APP_NAME,
        "Falta el diccionario KANJIDIC2 (data/kanjidic2.sqlite).\n\n"
        "¿Descargarlo ahora? (≈1,5 MB, solo esta vez)\n\n"
        "También podés generarlo con:  python -m yomitoru.setup_dict",
    ):
        return None
    from .setup_dict import main as setup_main
    try:
        setup_main([])
    except Exception as e:  # noqa: BLE001
        messagebox.showerror(APP_NAME, f"No se pudo descargar KANJIDIC2:\n{e}")
        return None
    return find_db()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="yomitoru", description="OCR de kanji desde el portapapeles.")
    parser.add_argument("--ocr", default="windows", choices=["windows", "manga"], help="motor de OCR")
    parser.add_argument("--interval", type=int, default=500, help="ms entre revisiones del portapapeles")
    parser.add_argument("--no-tray", action="store_true", help="sin ícono en la bandeja")
    args = parser.parse_args(argv)

    _enable_dpi_awareness()
    root = tk.Tk()
    if _already_running():
        root.withdraw()
        messagebox.showinfo(APP_NAME, "Yomitoru ya está abierto (buscalo en la bandeja del sistema).")
        root.destroy()
        return 0
    db_path = _ensure_dictionary(root)
    if db_path is None:
        root.destroy()
        return 1
    YomitoruApp(root, KanjiDictionary(db_path), create_engine(args.ocr),
                interval_ms=args.interval, use_tray=not args.no_tray)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
