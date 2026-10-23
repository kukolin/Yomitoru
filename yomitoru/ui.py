"""Ventana principal (Tkinter), historial y «Acerca de…»."""

from __future__ import annotations

import tkinter as tk
import webbrowser
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

from PIL import Image, ImageTk

from . import APP_NAME, AUTHOR, REPO_URL, __version__
from .history import format_when
from .lookup import KanjiEntry, LookupResult
from .settings import Settings
from .theme import Theme, apply_ttk, get_theme, set_titlebar, style_menu
from .tray import make_icon_image

if TYPE_CHECKING:
    from .app import YomitoruApp

JP_FONTS = ("Yu Gothic UI", "Yu Gothic", "Meiryo UI", "Meiryo", "MS Gothic")
LICENSE_URL = "https://www.edrdg.org/edrdg/licence.html"
KANJIDIC_URL = "https://www.edrdg.org/wiki/index.php/KANJIDIC_Project"
WAITING = "Esperando una captura (Win+Shift+S)…"


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
        # bind_all recibe la rueda de todas las ventanas: solo reaccionar dentro de este frame
        if not str(event.widget).startswith(str(self)):
            return
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-event.delta // 120, "units")

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)


def link(master, text: str, url: str, font, theme: Theme, bg: str | None = None) -> tk.Label:
    lbl = tk.Label(master, text=text, fg=theme.link, bg=bg or theme.bg, cursor="hand2", font=font,
                   borderwidth=0, padx=0, pady=0)
    lbl.bind("<Button-1>", lambda e: webbrowser.open(url))
    return lbl


class MainWindow:
    def __init__(self, root: tk.Tk | tk.Toplevel, app: YomitoruApp, on_close: Callable[[], None],
                 dict_meta: dict[str, str] | None = None):
        self.root = root
        self.app = app
        self.dict_meta = dict_meta or {}
        self._thumb = None
        self._result: LookupResult | None = None
        self._about: tk.Toplevel | None = None
        self.history_window: HistoryWindow | None = None

        jp = pick_font(root)
        self.f_big = tkfont.Font(family=jp, size=40)
        self.f_title = tkfont.Font(family=jp, size=16, weight="bold")
        self.f_entry = tkfont.Font(family=jp, size=15)
        self.f_text = tkfont.Font(family=jp, size=11)
        self.f_bold = tkfont.Font(family=jp, size=11, weight="bold")
        self.f_small = tkfont.Font(family=jp, size=9)
        self.style = ttk.Style(root)

        root.title(f"{APP_NAME} 読み取る")
        self._icon = ImageTk.PhotoImage(make_icon_image(32), master=root)
        root.iconphoto(True, self._icon)
        self._about_icon = ImageTk.PhotoImage(make_icon_image(56), master=root)
        root.geometry("460x620")
        root.minsize(380, 320)
        root.protocol("WM_DELETE_WINDOW", on_close)
        root.bind("<Escape>", lambda e: self.hide())
        root.bind("<Alt-Left>", lambda e: self.app.history_back())
        root.bind("<Alt-Right>", lambda e: self.app.history_forward())
        root.bind("<Control-h>", lambda e: self.show_history())

        # --- barra superior: ◀ ▶ Historial ........ Opciones ▾  Acerca de…
        top = ttk.Frame(root, padding=(8, 8, 8, 6))
        top.pack(fill="x")
        self.back_btn = ttk.Button(top, text="◀", style="Nav.TButton", command=self.app.history_back)
        self.back_btn.pack(side="left")
        self.fwd_btn = ttk.Button(top, text="▶", style="Nav.TButton", command=self.app.history_forward)
        self.fwd_btn.pack(side="left", padx=(2, 6))
        ttk.Button(top, text="Historial", command=self.show_history).pack(side="left")
        ttk.Button(top, text="Acerca de…", command=self.show_about).pack(side="right")
        options = ttk.Menubutton(top, text="Opciones")
        options.pack(side="right", padx=6)
        self.options_menu = tk.Menu(options, tearoff=False)
        options["menu"] = self.options_menu
        self.option_vars: dict[str, tk.BooleanVar] = {}
        for name, label in Settings.LABELS.items():
            var = tk.BooleanVar(value=getattr(self.app.settings, name))
            self.option_vars[name] = var
            self.options_menu.add_checkbutton(
                label=label, variable=var, command=lambda n=name, v=var: self.app.set_option(n, v.get()))
            if name in ("always_on_top", "show_english"):  # separar grupos: captura / ventana / historial
                self.options_menu.add_separator()

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

        self.word_row = ttk.Frame(root, padding=(8, 6))
        self.word_row.pack(fill="x")

        self.status_var = tk.StringVar(value=WAITING)
        ttk.Label(root, textvariable=self.status_var, style="Muted.TLabel",
                  padding=(8, 4)).pack(fill="x", side="bottom")

        self.scroll = ScrollFrame(root)
        self.scroll.pack(fill="both", expand=True, padx=8)

        self.apply_theme()
        self.apply_topmost()
        self.update_nav()

    @property
    def theme(self) -> Theme:
        return get_theme(self.app.settings.dark_mode)

    # --- acciones
    def _search(self):
        self.app.search(self.text_var.get())

    def apply_topmost(self):
        self.root.attributes("-topmost", self.app.settings.always_on_top)

    def sync_option(self, name: str, value: bool):
        self.option_vars[name].set(value)

    def apply_theme(self):
        t = self.theme
        apply_ttk(self.style, t, self.f_text, self.f_small, self.f_text.metrics("linespace") + 10)
        style_menu(self.options_menu, t)
        self.root.configure(bg=t.bg)
        self.scroll.canvas.configure(bg=t.bg)
        set_titlebar(self.root, t.dark)
        if self.history_window and self.history_window.exists():
            set_titlebar(self.history_window.win, t.dark)
        if self._about is not None and self._about.winfo_exists():
            self._about.destroy()  # tiene widgets tk con colores fijos: se vuelve a crear
            self.show_about()
        self.rerender()

    def update_nav(self):
        history = self.app.history
        self.back_btn.state(["!disabled"] if history.can_back() else ["disabled"])
        self.fwd_btn.state(["!disabled"] if history.can_forward() else ["disabled"])
        if self.history_window and self.history_window.exists():
            self.history_window.refresh()

    def set_status(self, text: str):
        self.status_var.set(text)

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
        self.root.after(300, self.apply_topmost)

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
        self._result = result
        self.rerender()

    def rerender(self):
        """Dibuja el último resultado (también al cambiar el tema o las opciones)."""
        for child in self.word_row.winfo_children():
            child.destroy()
        self.scroll.clear()
        result = self._result
        if result is None:
            return
        t = self.theme
        if result.word_url:
            ttk.Label(self.word_row, text="Palabra completa:", style="Muted.TLabel").pack(side="left")
            link(self.word_row, f"{result.text} en jisho.org", result.word_url, self.f_text, t).pack(
                side="left", padx=4)
        if not result.text:
            ttk.Label(self.scroll.inner, text="No se reconoció texto. Escribilo arriba y presioná Buscar.",
                      style="Muted.TLabel", font=self.f_text, padding=10).pack(anchor="w")
        elif not result.kanji:
            ttk.Label(self.scroll.inner, text="No hay kanji en el texto (solo kana o signos).",
                      style="Muted.TLabel", font=self.f_text, padding=10).pack(anchor="w")
        for entry in result.kanji:
            self._kanji_card(entry, t)

    def _kanji_card(self, entry: KanjiEntry, t: Theme):
        card = tk.Frame(self.scroll.inner, bg=t.card, highlightbackground=t.border, highlightthickness=1)
        card.pack(fill="x", pady=4)
        tk.Label(card, text=entry.literal, font=self.f_big, bg=t.card, fg=t.fg).grid(
            row=0, column=0, rowspan=5, sticky="n", padx=(10, 12), pady=6)
        body = tk.Frame(card, bg=t.card)
        body.grid(row=0, column=1, sticky="nwe", pady=6, padx=(0, 8))
        card.columnconfigure(1, weight=1)
        label_width = self.f_bold.measure("Significado") + 8
        body.columnconfigure(0, minsize=label_width)
        body.columnconfigure(1, weight=1)
        values: list[tk.Label] = []

        def field(label: str, value: str, muted=False, font=None):
            row = body.grid_size()[1]
            tk.Label(body, text=label, font=self.f_bold, bg=t.card, fg=t.fg, anchor="nw").grid(
                row=row, column=0, sticky="nw")
            lbl = tk.Label(body, text=value or "—", font=font or self.f_text, bg=t.card,
                           fg=t.muted if muted else t.fg, justify="left", anchor="w")
            lbl.grid(row=row, column=1, sticky="we")
            values.append(lbl)

        # ajustar el texto largo al ancho disponible (también al redimensionar)
        body.bind("<Configure>", lambda e: [v.configure(wraplength=max(100, e.width - label_width - 4))
                                            for v in values])

        info = entry.info
        if info is None:
            field("", "No está en KANJIDIC2", muted=True)
        else:
            field("On", "、".join(info.onyomi))
            field("Kun", "、".join(info.kunyomi))
            lang, meanings = info.meanings
            field("Significado", ", ".join(meanings))
            if lang == "es" and info.meanings_en and self.app.settings.show_english:
                field("", ", ".join(info.meanings_en), muted=True, font=self.f_small)
            extra = []
            if info.strokes:
                extra.append(f"{info.strokes} trazos")
            if info.jlpt:
                extra.append(f"JLPT {info.jlpt} (antiguo)")
            if info.grade:
                extra.append(f"grado {info.grade}")
            if extra:
                field("", " · ".join(extra), muted=True, font=self.f_small)
        link(body, "Ver en jisho.org", entry.url, self.f_small, t, bg=t.card).grid(
            row=body.grid_size()[1], column=0, columnspan=2, sticky="w", pady=(4, 0))

    # --- historial
    def show_history(self):
        if self.history_window and self.history_window.exists():
            self.history_window.win.deiconify()
            self.history_window.win.lift()
            self.history_window.win.focus_force()
            return
        self.history_window = HistoryWindow(self)

    # --- acerca de
    def show_about(self):
        if self._about is not None and self._about.winfo_exists():
            self._about.lift()
            self._about.focus_force()
            return
        t = self.theme
        win = self._about = tk.Toplevel(self.root, bg=t.bg)
        win.title(f"Acerca de {APP_NAME}")
        win.resizable(False, False)
        win.transient(self.root)
        win.bind("<Escape>", lambda e: win.destroy())
        set_titlebar(win, t.dark)
        frm = ttk.Frame(win, padding=18)
        frm.pack()
        width = 400

        def text(value, font=None, muted=False, pady=(0, 0)):
            ttk.Label(frm, text=value, font=font or self.f_text, foreground=t.muted if muted else t.fg,
                      wraplength=width, justify="left").pack(anchor="w", pady=pady)

        def heading(value):
            text(value, self.f_bold, pady=(14, 2))

        def links(*items):
            frame = ttk.Frame(frm)
            frame.pack(anchor="w", pady=(2, 0))
            for i, (label, url) in enumerate(items):
                if i:
                    ttk.Label(frame, text="·", foreground=t.muted).pack(side="left", padx=6)
                link(frame, label, url, self.f_text, t).pack(side="left")

        head = ttk.Frame(frm)
        head.pack(anchor="w", fill="x")
        ttk.Label(head, image=self._about_icon).pack(side="left", padx=(0, 12))
        titles = ttk.Frame(head)
        titles.pack(side="left")
        ttk.Label(titles, text=f"{APP_NAME} 読み取る", font=self.f_title).pack(anchor="w")
        ttk.Label(titles, text=f"Versión {__version__}", style="Muted.TLabel").pack(anchor="w")

        text("Capturá un kanji con Win+Shift+S y mirá al instante sus lecturas y su significado. "
             "Funciona sin conexión: el OCR es el de Windows y el diccionario viene incluido.", pady=(12, 0))

        heading("Autor")
        text(f"Creado por {AUTHOR}.")
        links(("Código fuente", REPO_URL), ("Nuevas versiones", f"{REPO_URL}/releases"),
              ("Reportar un error", f"{REPO_URL}/issues"))

        heading("Diccionario")
        version = self.dict_meta.get("database_version", "?")
        text("Este programa usa el archivo KANJIDIC2 (versión " + version + "), propiedad del "
             "Electronic Dictionary Research and Development Group (EDRDG), y se usa de acuerdo "
             "con su licencia: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0).")
        links(("Proyecto KANJIDIC", KANJIDIC_URL), ("Licencia del EDRDG", LICENSE_URL))

        heading("Licencia y créditos")
        text(f"Código bajo licencia MIT © 2026 {AUTHOR}.")
        text("OCR: Windows.Media.Ocr (Microsoft) vía pywinrt. Interfaz: Tkinter, Pillow y pystray. "
             "Los links abren Jisho.org.", self.f_small, muted=True, pady=(4, 0))

        ttk.Button(frm, text="Cerrar", command=win.destroy).pack(anchor="e", pady=(16, 0))
        win.focus_force()


class HistoryWindow:
    """Lista de búsquedas anteriores (la más nueva arriba). Doble clic o Enter para abrir."""

    def __init__(self, main: MainWindow):
        self.main = main
        self.app = main.app
        t = main.theme
        win = self.win = tk.Toplevel(main.root, bg=t.bg)
        win.title(f"Historial · {APP_NAME}")
        win.geometry("380x460")
        win.minsize(300, 240)
        win.bind("<Escape>", lambda e: win.destroy())
        set_titlebar(win, t.dark)

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        buttons = ttk.Frame(frm)
        buttons.pack(fill="x", side="bottom", pady=(8, 0))
        ttk.Button(buttons, text="Abrir", command=self.open_selected).pack(side="left")
        self.clear_btn = ttk.Button(buttons, text="Borrar historial…", command=self.clear)
        self.clear_btn.pack(side="right")

        self.empty = ttk.Label(frm, text="Todavía no hay búsquedas.\nCapturá un kanji con Win+Shift+S.",
                               style="Muted.TLabel", font=main.f_text, justify="center")
        lst = ttk.Frame(frm)
        lst.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(lst, columns=("text", "when"), show="headings", selectmode="browse")
        self.tree.heading("text", text="Texto", anchor="w")
        self.tree.heading("when", text="Fecha", anchor="w")
        self.tree.column("text", width=220, stretch=True)
        self.tree.column("when", width=110, stretch=False)
        bar = ttk.Scrollbar(lst, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.open_selected())
        self.tree.bind("<Return>", lambda e: self.open_selected())
        self.refresh()
        self.tree.focus_set()

    def exists(self) -> bool:
        try:
            return bool(self.win.winfo_exists())
        except tk.TclError:
            return False

    def refresh(self):
        history = self.app.history
        self.tree.delete(*self.tree.get_children())
        for index in range(len(history.entries) - 1, -1, -1):
            e = history.entries[index]
            self.tree.insert("", "end", iid=str(index), values=(e.text, format_when(e.when)))
        if history.entries:
            self.empty.place_forget()
            self.clear_btn.state(["!disabled"])
        else:
            self.empty.place(relx=0.5, rely=0.4, anchor="center")
            self.empty.lift()  # la lista se creó después y quedaría encima
            self.clear_btn.state(["disabled"])
        if history.pos is not None and self.tree.exists(str(history.pos)):
            iid = str(history.pos)
            self.tree.selection_set(iid)
            self.tree.focus(iid)
            self.tree.see(iid)

    def open_selected(self):
        selection = self.tree.selection()
        if selection:
            self.app.open_history(int(selection[0]))

    def clear(self):
        if messagebox.askyesno("Borrar historial", "¿Borrar todas las búsquedas del historial?",
                               parent=self.win):
            self.app.clear_history()
