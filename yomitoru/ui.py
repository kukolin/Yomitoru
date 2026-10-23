"""Ventana principal (Tkinter)."""

from __future__ import annotations

import tkinter as tk
import webbrowser
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageTk

from . import APP_NAME, AUTHOR, REPO_URL, __version__
from .lookup import KanjiEntry, LookupResult
from .tray import make_icon_image

JP_FONTS = ("Yu Gothic UI", "Yu Gothic", "Meiryo UI", "Meiryo", "MS Gothic")
LINK_COLOR = "#1a6fd1"
MUTED = "#6b6b6b"
LICENSE_URL = "https://www.edrdg.org/edrdg/licence.html"
KANJIDIC_URL = "https://www.edrdg.org/wiki/index.php/KANJIDIC_Project"


def pick_font(root: tk.Misc) -> str:
    available = set(tkfont.families(root))
    return next((f for f in JP_FONTS if f in available), "TkDefaultFont")


class ScrollFrame(ttk.Frame):
    """Frame con scroll vertical (Tk no trae uno)."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.bind_all("<MouseWheel>", self._on_wheel, add="+")

    def _on_wheel(self, event):
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-event.delta // 120, "units")

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)


def link(master, text: str, url: str, font) -> tk.Label:
    lbl = tk.Label(master, text=text, fg=LINK_COLOR, cursor="hand2", font=font, bg=master["bg"] if "bg" in master.keys() else None)
    lbl.bind("<Button-1>", lambda e: webbrowser.open(url))
    return lbl


class MainWindow:
    def __init__(self, root: tk.Tk, on_search: Callable[[str], None],
                 on_watch_toggle: Callable[[bool], None], on_close: Callable[[], None],
                 dict_meta: dict[str, str] | None = None):
        self.root = root
        self.on_search = on_search
        self.on_watch_toggle = on_watch_toggle
        self.dict_meta = dict_meta or {}
        self._thumb = None

        jp = pick_font(root)
        self.f_big = tkfont.Font(family=jp, size=40)
        self.f_title = tkfont.Font(family=jp, size=16, weight="bold")
        self.f_entry = tkfont.Font(family=jp, size=15)
        self.f_text = tkfont.Font(family=jp, size=11)
        self.f_bold = tkfont.Font(family=jp, size=11, weight="bold")
        self.f_small = tkfont.Font(family=jp, size=9)

        root.title(f"{APP_NAME} 読み取る")
        self._icon = ImageTk.PhotoImage(make_icon_image(32), master=root)
        root.iconphoto(True, self._icon)
        self._about_icon = ImageTk.PhotoImage(make_icon_image(56), master=root)
        self._about = None
        root.geometry("440x600")
        root.minsize(340, 300)
        root.protocol("WM_DELETE_WINDOW", on_close)
        root.bind("<Escape>", lambda e: self.hide())

        style = ttk.Style(root)
        style.configure("Card.TFrame", background="white")
        style.configure("TCheckbutton", font=self.f_small)

        # --- barra superior
        top = ttk.Frame(root, padding=(8, 6))
        top.pack(fill="x")
        self.topmost_var = tk.BooleanVar(value=False)
        self.watch_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Siempre visible", variable=self.topmost_var,
                        command=self._apply_topmost).pack(side="left")
        ttk.Checkbutton(top, text="Vigilar portapapeles", variable=self.watch_var,
                        command=lambda: self.on_watch_toggle(self.watch_var.get())).pack(side="left", padx=8)
        ttk.Button(top, text="Acerca de…", command=self.show_about).pack(side="right")

        # --- texto reconocido (editable) + captura
        row = ttk.Frame(root, padding=(8, 0))
        row.pack(fill="x")
        self.thumb_label = ttk.Label(row)
        self.thumb_label.pack(side="left", padx=(0, 6))
        self.text_var = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.text_var, font=self.f_entry)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self._search())
        ttk.Button(row, text="Buscar", command=self._search).pack(side="left", padx=(6, 0))
        self.entry = entry

        self.word_row = ttk.Frame(root, padding=(8, 4))
        self.word_row.pack(fill="x")

        self.scroll = ScrollFrame(root)
        self.scroll.pack(fill="both", expand=True, padx=8)

        self.status_var = tk.StringVar(value="Esperando una captura (Win+Shift+S)…")
        ttk.Label(root, textvariable=self.status_var, foreground=MUTED, font=self.f_small,
                  padding=(8, 4)).pack(fill="x", side="bottom")

    # --- acciones
    def _search(self):
        self.on_search(self.text_var.get())

    def _apply_topmost(self):
        self.root.attributes("-topmost", self.topmost_var.get())

    def set_status(self, text: str):
        self.status_var.set(text)

    def set_watching(self, watching: bool):
        self.watch_var.set(watching)

    def hide(self):
        self.root.withdraw()

    def bring_to_front(self):
        self.root.deiconify()
        if self.root.state() == "iconic":
            self.root.state("normal")
        # Windows no deja robar el foco libremente: topmost momentáneo para que aparezca encima
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        self.root.after(300, self._apply_topmost)

    def set_capture(self, image: Image.Image | None):
        if image is None:
            self.thumb_label.configure(image="")
            self._thumb = None
            return
        thumb = image.copy()
        thumb.thumbnail((90, 40))
        self._thumb = ImageTk.PhotoImage(thumb, master=self.root)
        self.thumb_label.configure(image=self._thumb)

    def set_text(self, text: str):
        self.text_var.set(text)

    # --- resultados
    def show_result(self, result: LookupResult):
        for child in self.word_row.winfo_children():
            child.destroy()
        if result.word_url:
            ttk.Label(self.word_row, text="Palabra completa:", font=self.f_small).pack(side="left")
            link(self.word_row, f"{result.text} en jisho.org", result.word_url, self.f_text).pack(side="left", padx=4)

        self.scroll.clear()
        if not result.text:
            ttk.Label(self.scroll.inner, text="No se reconoció texto. Escribilo arriba y presioná Buscar.",
                      font=self.f_text, foreground=MUTED, padding=10).pack(anchor="w")
        elif not result.kanji:
            ttk.Label(self.scroll.inner, text="No hay kanji en el texto (solo kana o signos).",
                      font=self.f_text, foreground=MUTED, padding=10).pack(anchor="w")
        for entry in result.kanji:
            self._kanji_card(entry)

    def _kanji_card(self, entry: KanjiEntry):
        card = tk.Frame(self.scroll.inner, bg="white", highlightbackground="#dddddd", highlightthickness=1)
        card.pack(fill="x", pady=4)
        tk.Label(card, text=entry.literal, font=self.f_big, bg="white").grid(row=0, column=0, rowspan=5,
                                                                           sticky="n", padx=(10, 12), pady=6)
        body = tk.Frame(card, bg="white")
        body.grid(row=0, column=1, sticky="nwe", pady=6, padx=(0, 8))
        card.columnconfigure(1, weight=1)
        label_width = self.f_bold.measure("Significado") + 8
        body.columnconfigure(0, minsize=label_width)
        body.columnconfigure(1, weight=1)
        values: list[tk.Label] = []

        def field(label: str, value: str, color=None, font=None):
            row = body.grid_size()[1]
            tk.Label(body, text=label, font=self.f_bold, bg="white", anchor="nw").grid(row=row, column=0, sticky="nw")
            lbl = tk.Label(body, text=value or "—", font=font or self.f_text, bg="white", fg=color or "black",
                           justify="left", anchor="w")
            lbl.grid(row=row, column=1, sticky="we")
            values.append(lbl)

        # ajustar el texto largo al ancho disponible (también al redimensionar)
        body.bind("<Configure>", lambda e: [v.configure(wraplength=max(100, e.width - label_width - 4))
                                            for v in values])

        info = entry.info
        if info is None:
            field("", "No está en KANJIDIC2", MUTED)
        else:
            field("On", "、".join(info.onyomi))
            field("Kun", "、".join(info.kunyomi))
            lang, meanings = info.meanings
            field("Significado", ", ".join(meanings))
            if lang == "es" and info.meanings_en:
                field("", ", ".join(info.meanings_en), MUTED, self.f_small)
            extra = []
            if info.strokes:
                extra.append(f"{info.strokes} trazos")
            if info.jlpt:
                extra.append(f"JLPT {info.jlpt} (antiguo)")
            if info.grade:
                extra.append(f"grado {info.grade}")
            if extra:
                field("", " · ".join(extra), MUTED, self.f_small)
        link(body, "Ver en jisho.org", entry.url, self.f_small).grid(row=body.grid_size()[1], column=0,
                                                                     columnspan=2, sticky="w", pady=(4, 0))

    # --- acerca de
    def show_about(self):
        if self._about is not None and self._about.winfo_exists():
            self._about.lift()
            self._about.focus_force()
            return
        win = self._about = tk.Toplevel(self.root)
        win.title(f"Acerca de {APP_NAME}")
        win.resizable(False, False)
        win.transient(self.root)
        win.bind("<Escape>", lambda e: win.destroy())
        frm = ttk.Frame(win, padding=18)
        frm.pack()
        width = 400

        def text(value, font=None, color=None, pady=(0, 0)):
            ttk.Label(frm, text=value, font=font or self.f_text, foreground=color, wraplength=width,
                      justify="left").pack(anchor="w", pady=pady)

        def heading(value):
            text(value, self.f_bold, pady=(14, 2))

        head = ttk.Frame(frm)
        head.pack(anchor="w", fill="x")
        ttk.Label(head, image=self._about_icon).pack(side="left", padx=(0, 12))
        titles = ttk.Frame(head)
        titles.pack(side="left")
        ttk.Label(titles, text=f"{APP_NAME} 読み取る", font=self.f_title).pack(anchor="w")
        ttk.Label(titles, text=f"Versión {__version__}", font=self.f_small, foreground=MUTED).pack(anchor="w")

        text("Capturá un kanji con Win+Shift+S y mirá al instante sus lecturas y su significado. "
             "Funciona sin conexión: el OCR es el de Windows y el diccionario viene incluido.", pady=(12, 0))

        heading("Autor")
        text(f"Creado por {AUTHOR}.")
        links = ttk.Frame(frm)
        links.pack(anchor="w", pady=(2, 0))
        link(links, "Código fuente", REPO_URL, self.f_text).pack(side="left")
        ttk.Label(links, text="·", foreground=MUTED).pack(side="left", padx=6)
        link(links, "Nuevas versiones", f"{REPO_URL}/releases", self.f_text).pack(side="left")
        ttk.Label(links, text="·", foreground=MUTED).pack(side="left", padx=6)
        link(links, "Reportar un error", f"{REPO_URL}/issues", self.f_text).pack(side="left")

        heading("Diccionario")
        version = self.dict_meta.get("database_version", "?")
        text("Este programa usa el archivo KANJIDIC2 (versión " + version + "), propiedad del "
             "Electronic Dictionary Research and Development Group (EDRDG), y se usa de acuerdo "
             "con su licencia: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0).")
        links = ttk.Frame(frm)
        links.pack(anchor="w", pady=(2, 0))
        link(links, "Proyecto KANJIDIC", KANJIDIC_URL, self.f_text).pack(side="left")
        ttk.Label(links, text="·", foreground=MUTED).pack(side="left", padx=6)
        link(links, "Licencia del EDRDG", LICENSE_URL, self.f_text).pack(side="left")

        heading("Licencia y créditos")
        text(f"Código bajo licencia MIT © 2026 {AUTHOR}.")
        text("OCR: Windows.Media.Ocr (Microsoft) vía pywinrt. Interfaz: Tkinter, Pillow y pystray. "
             "Los links abren Jisho.org.", self.f_small, MUTED, pady=(4, 0))

        ttk.Button(frm, text="Cerrar", command=win.destroy).pack(anchor="e", pady=(16, 0))
        win.focus_force()
