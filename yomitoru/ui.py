"""Main window (Tkinter), history and About."""

from __future__ import annotations

import ctypes
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

from PIL import Image, ImageDraw, ImageTk

from . import APP_NAME, AUTHOR, REPO_URL, __version__
from .i18n import LANGUAGES
from .lookup import KanjiEntry, LookupResult, jisho_word_url
from .settings import Settings
from .theme import Theme, apply_ttk, get_theme, set_titlebar, style_menu
from .tray import make_icon_image

if TYPE_CHECKING:
    from .app import YomitoruApp

JP_FONTS = ("Yu Gothic UI", "Yu Gothic", "Meiryo UI", "Meiryo", "MS Gothic")
LICENSE_URL = "https://www.edrdg.org/edrdg/licence.html"
KANJIDIC_URL = "https://www.edrdg.org/wiki/index.php/KANJIDIC_Project"


def pick_font(root: tk.Misc) -> str:
    available = set(tkfont.families(root))
    return next((f for f in JP_FONTS if f in available), "TkDefaultFont")


class ScrollFrame(ttk.Frame):
    """Frame with a vertical scrollbar (Tk has none built in)."""

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
        # bind_all gets the wheel from every window: only react inside this frame
        if not self.winfo_exists() or not str(event.widget).startswith(str(self)):
            return
        if isinstance(event.widget, tk.Text):
            return  # SelectableText already forwarded it to on_wheel
        self.on_wheel(event)

    def on_wheel(self, event):
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-event.delta // 120, "units")

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)


def link(master, text: str, command: Callable[[], None] | str, font, theme: Theme,
         bg: str | None = None) -> tk.Label:
    """Clickable text. `command` is a URL or a function."""
    lbl = tk.Label(master, text=text, fg=theme.link, bg=bg or theme.bg, cursor="hand2", font=font,
                   borderwidth=0, padx=0, pady=0)
    action = (lambda: webbrowser.open(command)) if isinstance(command, str) else command
    lbl.bind("<Button-1>", lambda e: action())
    return lbl


def place_over(win: tk.Toplevel, parent: tk.Misc, width: int | None = None, height: int | None = None):
    """Center `win` over `parent`, kept inside the work area of the parent's monitor."""
    win.update_idletasks()
    w, h = width or win.winfo_reqwidth(), height or win.winfo_reqheight()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    x, y = px + (pw - w) // 2, py + max(0, (ph - h) // 2)
    left, top, right, bottom = _work_area(px + pw // 2, py + ph // 2, win)
    x = max(left, min(x, right - w))
    y = max(top, min(y, bottom - h - 32))  # 32: room for the title bar
    win.geometry(f"{w}x{h}+{x}+{y}")


def _work_area(x: int, y: int, win: tk.Misc) -> tuple[int, int, int, int]:
    """Work area (screen minus taskbar) of the monitor that contains the point (x, y)."""
    try:
        import ctypes.wintypes as wt

        class MonitorInfo(ctypes.Structure):
            _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT), ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]

        user32 = ctypes.windll.user32
        user32.MonitorFromPoint.restype = ctypes.c_void_p
        monitor = user32.MonitorFromPoint(wt.POINT(x, y), 2)  # MONITOR_DEFAULTTONEAREST
        info = MonitorInfo(cbSize=ctypes.sizeof(MonitorInfo))
        if user32.GetMonitorInfoW(ctypes.c_void_p(monitor), ctypes.byref(info)):
            r = info.rcWork
            return r.left, r.top, r.right, r.bottom
    except (AttributeError, OSError):
        pass
    return 0, 0, win.winfo_screenwidth(), win.winfo_screenheight()


def dot_image(color: str, filled: bool, size: int, master) -> ImageTk.PhotoImage:
    """Smooth circle: drawn 4x larger and scaled down (Tk canvases draw jagged circles)."""
    scale = 4
    big = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    margin = scale  # 1 px of room so the edge is never clipped
    box = (margin, margin, size * scale - margin - 1, size * scale - margin - 1)
    draw = ImageDraw.Draw(big)
    if filled:
        draw.ellipse(box, fill=color)
    else:
        draw.ellipse(box, outline=color, width=int(1.6 * scale))
    return ImageTk.PhotoImage(big.resize((size, size), Image.LANCZOS), master=master)


def copy_icon(color: str, size: int, master, done: bool = False) -> ImageTk.PhotoImage:
    """Smooth "copy" icon (two overlapping sheets), or a check mark when `done`."""
    scale = 4
    s = size * scale
    big = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(big)
    width = max(scale, int(1.6 * scale))
    if done:
        draw.line([(s * 0.18, s * 0.52), (s * 0.42, s * 0.76), (s * 0.84, s * 0.26)], fill=color, width=width * 2,
                  joint="curve")
    else:
        radius = int(s * 0.12)
        draw.rounded_rectangle((s * 0.34, s * 0.06, s * 0.92, s * 0.70), radius, outline=color, width=width)
        draw.rounded_rectangle((s * 0.10, s * 0.30, s * 0.68, s * 0.94), radius, outline=color, width=width,
                               fill=None)
    return ImageTk.PhotoImage(big.resize((size, size), Image.LANCZOS), master=master)


class Tooltip:
    """Small hint shown after hovering a widget for a moment."""

    def __init__(self, widget: tk.Widget, text: Callable[[], str], theme: Callable[[], Theme], font):
        self.widget, self.text, self.theme, self.font = widget, text, theme, font
        self.tip: tk.Toplevel | None = None
        self.job = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def _schedule(self, _event=None):
        self.hide()
        self.job = self.widget.after(500, self._show)

    def _show(self):
        if not self.widget.winfo_exists():
            return
        t = self.theme()
        self.tip = tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        tip.attributes("-topmost", True)
        tk.Label(tip, text=self.text(), font=self.font, bg=t.card, fg=t.fg, padx=6, pady=2,
                 highlightbackground=t.border, highlightthickness=1).pack()
        tip.geometry(f"+{self.widget.winfo_rootx()}+{self.widget.winfo_rooty() + self.widget.winfo_height() + 4}")

    def hide(self, _event=None):
        if self.job:
            self.widget.after_cancel(self.job)
            self.job = None
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class SelectableText(tk.Text):
    """Read-only text that looks like a label but can be selected and copied (Ctrl+C or right-click).

    Its height follows the number of wrapped lines, and the mouse wheel scrolls the results list
    instead of the text itself.
    """

    def __init__(self, master, value: str, font, theme: Theme, fg: str, main: MainWindow,
                 justify: str = "left", width: int = 1):
        super().__init__(master, font=font, bg=theme.card, fg=fg, wrap="word", width=width, height=1,
                         borderwidth=0, highlightthickness=0, padx=0, pady=0, cursor="xterm",
                         selectbackground=theme.select, selectforeground=theme.fg,
                         inactiveselectbackground=theme.select, insertwidth=0, spacing1=1, spacing3=1)
        self.tag_configure("all", justify=justify)
        self.insert("1.0", value, "all")
        # "disabled" blocks typing but still allows selecting and copying
        self.configure(state="disabled")
        self.main = main
        self.bind("<Configure>", self._fit_height)
        self.bind("<MouseWheel>", self._wheel)
        self.bind("<Button-3>", self._context_menu)

    def _fit_height(self, _event=None):
        lines = self.count("1.0", "end-1c", "displaylines")
        lines = max(1, (lines[0] if isinstance(lines, tuple) else lines or 0) + 1)
        if int(self.cget("height")) != lines:
            self.configure(height=lines)

    def _wheel(self, event):
        self.main.scroll.on_wheel(event)
        return "break"

    def _context_menu(self, event):
        selected = bool(self.tag_ranges("sel"))
        menu = tk.Menu(self, tearoff=False)
        style_menu(menu, self.main.theme)
        menu.add_command(label=self.main.t("copy"), command=lambda: self.main.copy_to_clipboard(
            self.get("sel.first", "sel.last") if selected else self.get("1.0", "end-1c")))
        menu.tk_popup(event.x_root, event.y_root)


class ListeningToggle(tk.Frame):
    """Prominent indicator of whether the app is listening to the clipboard; a click toggles it."""

    def __init__(self, master, main: MainWindow):
        super().__init__(master, cursor="hand2", padx=10, pady=4)
        self.main = main
        self.dot_size = max(9, round(main.f_bold.metrics("linespace") * 0.5))
        self.dot = tk.Label(self, cursor="hand2", borderwidth=0, padx=0, pady=0)
        self.dot.pack(side="left", padx=(0, 7))
        self.label = tk.Label(self, font=main.f_bold, cursor="hand2", borderwidth=0, padx=0, pady=0)
        self.label.pack(side="left")
        for widget in (self, self.dot, self.label):
            widget.bind("<Button-1>", lambda e: main.app.set_watching(not main.app.watching))
        self.refresh()

    def refresh(self):
        t, on = self.main.theme, self.main.app.watching
        bg, fg = (t.on_bg, t.on_fg) if on else (t.off_bg, t.off_fg)
        self.configure(bg=bg)
        self.label.configure(bg=bg, fg=fg, text=self.main.t("listening" if on else "off"))
        self._dot = dot_image(fg, on, self.dot_size, self)  # keep a reference or Tk drops the image
        self.dot.configure(bg=bg, image=self._dot)


class MainWindow:
    def __init__(self, root: tk.Tk | tk.Toplevel, app: YomitoruApp, on_close: Callable[[], None],
                 dict_meta: dict[str, str] | None = None):
        self.root = root
        self.app = app
        self.dict_meta = dict_meta or {}
        self._image: Image.Image | None = None
        self._thumb = None
        self._result: LookupResult | None = None
        self._status: tuple[str, dict] = ("waiting", {})
        self._about: tk.Toplevel | None = None
        self.history_window: HistoryWindow | None = None
        self.frame: ttk.Frame | None = None

        jp = pick_font(root)
        self.f_big = tkfont.Font(family=jp, size=40)
        self.f_title = tkfont.Font(family=jp, size=16, weight="bold")
        self.f_entry = tkfont.Font(family=jp, size=15)
        self.f_text = tkfont.Font(family=jp, size=11)
        self.f_bold = tkfont.Font(family=jp, size=11, weight="bold")
        self.f_small = tkfont.Font(family=jp, size=9)
        self.style = ttk.Style(root)
        self.text_var = tk.StringVar(master=root)
        self.status_var = tk.StringVar(master=root)

        root.title(f"{APP_NAME} 読み取る")
        self._icon = ImageTk.PhotoImage(make_icon_image(32), master=root)
        root.iconphoto(True, self._icon)
        self._about_icon = ImageTk.PhotoImage(make_icon_image(56), master=root)
        root.geometry("500x620")
        root.protocol("WM_DELETE_WINDOW", on_close)
        root.bind("<Escape>", lambda e: self.hide())
        root.bind("<Alt-Left>", lambda e: self.app.history_back())
        root.bind("<Alt-Right>", lambda e: self.app.history_forward())
        root.bind("<Control-h>", lambda e: self.show_history())

        self._build()
        self.apply_theme()
        self.apply_topmost()

    @property
    def theme(self) -> Theme:
        return get_theme(self.app.settings.dark_mode)

    @property
    def t(self):
        return self.app.t

    # --- building (fully rebuilt when the language changes)
    def _build(self):
        if self.frame is not None:
            self.frame.destroy()
        t = self.t
        frame = self.frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        # row 1: [● Listening] ........ [History] [Options ▾] [About…]
        top = ttk.Frame(frame, padding=(8, 8, 8, 6))
        top.pack(fill="x")
        self.listening = ListeningToggle(top, self)
        self.listening.pack(side="left")
        ttk.Button(top, text=t("about_btn"), command=self.show_about).pack(side="right")
        options = ttk.Menubutton(top, text=t("options"))
        options.pack(side="right", padx=6)
        ttk.Button(top, text=t("history"), command=self.show_history).pack(side="right")
        self._build_options_menu(options)

        # row 2: [◀][▶] [screenshot] [recognized text, editable] [Search]
        row = ttk.Frame(frame, padding=(8, 0))
        row.pack(fill="x")
        self.back_btn = ttk.Button(row, text="◀", style="Nav.TButton", command=self.app.history_back)
        self.back_btn.pack(side="left")
        self.fwd_btn = ttk.Button(row, text="▶", style="Nav.TButton", command=self.app.history_forward)
        self.fwd_btn.pack(side="left", padx=(2, 6))
        self.thumb_label = ttk.Label(row)
        self.thumb_label.pack(side="left", padx=(0, 6))
        # the button is placed before the field: when space runs out the field shrinks, not the button
        ttk.Button(row, text=t("search_btn"), command=self._search).pack(side="right", padx=(6, 0))
        self.entry = ttk.Entry(row, textvariable=self.text_var, font=self.f_entry, width=10)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self._search())

        # row 3: jisho.org link with whatever is typed in the field
        self.links_row = ttk.Frame(frame, padding=(8, 6))
        self.links_row.pack(fill="x")

        ttk.Label(frame, textvariable=self.status_var, style="Muted.TLabel",
                  padding=(8, 4)).pack(fill="x", side="bottom")
        self.scroll = ScrollFrame(frame)
        self.scroll.pack(fill="both", expand=True, padx=8)

        self.set_capture(self._image)
        self.update_nav()
        self._render_status()
        self._fit_width(top)

    def _fit_width(self, toolbar: ttk.Frame):
        """Minimum width from the buttons in this language (German or Russian are longer)."""
        self.root.update_idletasks()
        needed = max(400, toolbar.winfo_reqwidth() + 4)
        self.root.minsize(needed, 320)
        if self.root.winfo_width() > 1 and self.root.winfo_width() < needed:
            self.root.geometry(f"{needed}x{self.root.winfo_height()}")

    def _build_options_menu(self, button: ttk.Menubutton):
        t = self.t
        menu = self.options_menu = tk.Menu(button, tearoff=False)
        button["menu"] = menu
        self.option_vars: dict[str, tk.BooleanVar] = {}
        for name, key in Settings.TOGGLES.items():
            var = tk.BooleanVar(master=self.root, value=getattr(self.app.settings, name))
            self.option_vars[name] = var
            menu.add_checkbutton(label=t(key), variable=var,
                                 command=lambda n=name, v=var: self.app.set_option(n, v.get()))
        menu.add_separator()
        languages = self.languages_menu = tk.Menu(menu, tearoff=False)
        self.language_var = tk.StringVar(master=self.root, value=self.app.settings.language)
        for code, name in LANGUAGES.items():
            languages.add_radiobutton(label=name, value=code, variable=self.language_var,
                                      command=lambda c=code: self.app.set_option("language", c))
        # in other languages also show "Language", so it can be found after picking one by mistake
        label = t("opt_language") if self.app.settings.language == "en" else f"{t('opt_language')} / Language"
        menu.add_cascade(label=label, menu=languages)

    def retranslate(self):
        """Rebuild the window in the new language (and any open secondary windows)."""
        self._build()
        self.apply_theme()
        if self.history_window and self.history_window.exists():
            self.history_window.win.destroy()
            self.history_window = HistoryWindow(self)

    # --- actions
    def _search(self):
        self.app.search(self.text_var.get())

    def _open_jisho(self):
        text = "".join(self.text_var.get().split())
        if text:
            webbrowser.open(jisho_word_url(text))

    def apply_topmost(self):
        self.root.attributes("-topmost", self.app.settings.always_on_top)

    def sync_option(self, name: str, value):
        if name in self.option_vars:
            self.option_vars[name].set(value)

    def update_listening(self):
        self.listening.refresh()

    def apply_theme(self):
        t = self.theme
        apply_ttk(self.style, t, self.f_text, self.f_small, self.f_text.metrics("linespace") + 10)
        style_menu(self.options_menu, t)
        style_menu(self.languages_menu, t)
        self.root.configure(bg=t.bg)
        self.scroll.canvas.configure(bg=t.bg)
        self.listening.refresh()
        set_titlebar(self.root, t.dark)
        if self.history_window and self.history_window.exists():
            set_titlebar(self.history_window.win, t.dark)
        if self._about is not None and self._about.winfo_exists():
            self._about.destroy()  # it has tk widgets with fixed colors: recreate it
            self.show_about()
        self.rerender()

    def update_nav(self):
        history = self.app.history
        self.back_btn.state(["!disabled"] if history.can_back() else ["disabled"])
        self.fwd_btn.state(["!disabled"] if history.can_forward() else ["disabled"])
        if self.history_window and self.history_window.exists():
            self.history_window.refresh()

    def set_status(self, key: str, **kwargs):
        """Store the key (not the text) so it can be translated if the language changes.
        A `when` datetime is formatted like «today 19:42» in the current language."""
        self._status = (key, kwargs)
        self._render_status()

    def _render_status(self):
        key, kwargs = self._status
        kwargs = {k: self.t.format_when(v) if isinstance(v, datetime) else v for k, v in kwargs.items()}
        self.status_var.set(self.t(key, **kwargs))

    def hide(self):
        self.root.withdraw()

    def bring_to_front(self):
        self.root.deiconify()
        if self.root.state() == "iconic":
            self.root.state("normal")
        # Windows does not let apps steal focus freely: briefly topmost so it shows on top
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        self.root.after(300, self.apply_topmost)

    def set_capture(self, image: Image.Image | None):
        self._image = image
        if image is None:
            self.thumb_label.configure(image="")
            self._thumb = None
            return
        thumb = image.copy()
        thumb.thumbnail((70, 36))
        self._thumb = ImageTk.PhotoImage(thumb, master=self.root)
        self.thumb_label.configure(image=self._thumb)

    def set_text(self, text: str):
        self.text_var.set(text)

    # --- results
    def show_result(self, result: LookupResult):
        self._result = result
        self.rerender()

    def rerender(self):
        """Draw the last result (also when the theme or language changes)."""
        for child in self.links_row.winfo_children():
            child.destroy()
        self.scroll.clear()
        t = self.theme
        link(self.links_row, self.t("search_jisho"), self._open_jisho, self.f_text, t).pack(side="right")
        result = self._result
        if result is None:
            return
        if not result.text:
            ttk.Label(self.scroll.inner, text=self.t("no_text"), style="Muted.TLabel", font=self.f_text,
                      padding=10).pack(anchor="w")
        elif not result.kanji:
            ttk.Label(self.scroll.inner, text=self.t("no_kanji"), style="Muted.TLabel", font=self.f_text,
                      padding=10).pack(anchor="w")
        for entry in result.kanji:
            self._kanji_card(entry, t)

    def _kanji_card(self, entry: KanjiEntry, t: Theme):
        tr, lang = self.t, self.app.settings.language
        card = tk.Frame(self.scroll.inner, bg=t.card, highlightbackground=t.border, highlightthickness=1)
        card.pack(fill="x", pady=4)

        # left column: the big kanji (selectable)
        side = tk.Frame(card, bg=t.card)
        side.grid(row=0, column=0, sticky="n", padx=(10, 12), pady=6)
        chars = -(-self.f_big.measure(entry.literal) // self.f_big.measure("0"))  # Text width is in "0"s
        SelectableText(side, entry.literal, self.f_big, t, t.fg, self, justify="center", width=chars).pack()

        # top-right corner: button that copies the kanji
        icon_size = max(16, round(self.f_text.metrics("linespace")))
        copy_btn = tk.Label(card, bg=t.card, cursor="hand2", borderwidth=0, padx=3, pady=3)
        copy_btn.image = copy_icon(t.muted, icon_size, copy_btn)
        copy_btn.configure(image=copy_btn.image)
        copy_btn.grid(row=0, column=2, sticky="ne", padx=(0, 6), pady=6)
        copy_btn.bind("<Button-1>", lambda e: self._copy_kanji(entry.literal, copy_btn, icon_size))
        copy_btn.bind("<Enter>", lambda e: copy_btn.configure(bg=t.button_hover))
        copy_btn.bind("<Leave>", lambda e: copy_btn.configure(bg=t.card))
        Tooltip(copy_btn, lambda: self.t("copy_kanji"), lambda: self.theme, self.f_small)

        body = tk.Frame(card, bg=t.card)
        body.grid(row=0, column=1, sticky="nwe", pady=6, padx=(0, 8))
        card.columnconfigure(1, weight=1)
        label_width = max(self.f_bold.measure(tr(k)) for k in ("on", "kun", "meaning")) + 12
        body.columnconfigure(0, minsize=label_width)
        body.columnconfigure(1, weight=1)

        def field(label: str, value: str, muted=False, font=None):
            row = body.grid_size()[1]
            tk.Label(body, text=label, font=self.f_bold, bg=t.card, fg=t.fg, anchor="nw").grid(
                row=row, column=0, sticky="nw")
            SelectableText(body, value or "—", font or self.f_text, t, t.muted if muted else t.fg, self).grid(
                row=row, column=1, sticky="we")

        info = entry.info
        if info is None:
            field("", tr("not_in_dict"), muted=True)
        else:
            field(tr("on"), "、".join(info.onyomi))
            field(tr("kun"), "、".join(info.kunyomi))
            meaning_lang, meanings = info.meanings_for(lang)
            field(tr("meaning"), ", ".join(meanings))
            if meaning_lang != lang and tr("meaning_in_english"):
                field("", tr("meaning_in_english"), muted=True, font=self.f_small)
            extra = []
            if info.strokes:
                extra.append(tr("strokes", n=info.strokes))
            if info.jlpt:
                extra.append(tr("jlpt", n=info.jlpt))
            if info.grade:
                extra.append(tr("grade", n=info.grade))
            if extra:
                field("", " · ".join(extra), muted=True, font=self.f_small)
        link(body, tr("view_jisho"), entry.url, self.f_small, t, bg=t.card).grid(
            row=body.grid_size()[1], column=0, columnspan=2, sticky="w", pady=(4, 0))

    def copy_to_clipboard(self, text: str):
        """Put text on the clipboard and say so in the status bar for a moment.
        Copying text does not trigger a lookup: the watcher only reacts to images."""
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        previous = self._status
        self.set_status("copied", text=text)
        self.root.after(2500, lambda: self._status[0] == "copied" and self.set_status(previous[0], **previous[1]))

    def _copy_kanji(self, literal: str, button: tk.Label, icon_size: int):
        self.copy_to_clipboard(literal)
        t = self.theme
        button.image = copy_icon(t.on_fg, icon_size, button, done=True)
        button.configure(image=button.image)

        def restore():
            if button.winfo_exists():
                button.image = copy_icon(self.theme.muted, icon_size, button)
                button.configure(image=button.image)

        self.root.after(1200, restore)

    # --- history
    def show_history(self):
        if self.history_window and self.history_window.exists():
            self.history_window.win.deiconify()
            self.history_window.win.lift()
            self.history_window.win.focus_force()
            return
        self.history_window = HistoryWindow(self)

    # --- about
    def show_about(self):
        if self._about is not None and self._about.winfo_exists():
            self._about.lift()
            self._about.focus_force()
            return
        t, tr = self.theme, self.t
        win = self._about = tk.Toplevel(self.root, bg=t.bg)
        win.withdraw()  # built hidden and shown already in place, over the main window
        win.title(tr("about_title", app=APP_NAME))
        win.resizable(False, False)
        win.transient(self.root)
        win.bind("<Escape>", lambda e: win.destroy())
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
        ttk.Label(titles, text=tr("about_version", version=__version__), style="Muted.TLabel").pack(anchor="w")

        text(tr("about_tagline"), pady=(12, 0))

        heading(tr("about_author"))
        text(tr("about_created_by", author=AUTHOR))
        links((tr("about_source"), REPO_URL), (tr("about_releases"), f"{REPO_URL}/releases"),
              (tr("about_report"), f"{REPO_URL}/issues"))

        heading(tr("about_dictionary"))
        text(tr("about_dict_text", version=self.dict_meta.get("database_version", "?")))
        links((tr("about_kanjidic"), KANJIDIC_URL), (tr("about_edrdg"), LICENSE_URL))

        heading(tr("about_license"))
        text(tr("about_code_license", author=AUTHOR))
        text(tr("about_credits"), self.f_small, muted=True, pady=(4, 0))

        ttk.Button(frm, text=tr("close"), command=win.destroy).pack(anchor="e", pady=(16, 0))
        place_over(win, self.root)
        win.deiconify()
        set_titlebar(win, t.dark)
        win.focus_force()


class HistoryWindow:
    """List of previous searches (newest first). Double-click or Enter to open."""

    def __init__(self, main: MainWindow):
        self.main = main
        self.app = main.app
        t, tr = main.theme, main.t
        win = self.win = tk.Toplevel(main.root, bg=t.bg)
        win.withdraw()  # built hidden and shown already in place, over the main window
        win.title(f"{tr('hist_title')} · {APP_NAME}")
        win.minsize(320, 240)
        win.bind("<Escape>", lambda e: win.destroy())

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)
        buttons = ttk.Frame(frm)
        buttons.pack(fill="x", side="bottom", pady=(8, 0))
        ttk.Button(buttons, text=tr("hist_open"), command=self.open_selected).pack(side="left")
        self.clear_btn = ttk.Button(buttons, text=tr("hist_clear"), command=self.clear)
        self.clear_btn.pack(side="right")

        self.empty = ttk.Label(frm, text=tr("hist_empty"), style="Muted.TLabel", font=main.f_text,
                               justify="center")
        lst = ttk.Frame(frm)
        lst.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(lst, columns=("text", "when"), show="headings", selectmode="browse")
        self.tree.heading("text", text=tr("hist_col_text"), anchor="w")
        self.tree.heading("when", text=tr("hist_col_when"), anchor="w")
        self.tree.column("text", width=230, stretch=True)
        self.tree.column("when", width=130, stretch=False)
        bar = ttk.Scrollbar(lst, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.open_selected())
        self.tree.bind("<Return>", lambda e: self.open_selected())
        self.refresh()
        place_over(win, main.root, 400, 460)
        win.deiconify()
        set_titlebar(win, t.dark)
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
            self.tree.insert("", "end", iid=str(index), values=(e.text, self.main.t.format_when(e.when)))
        if history.entries:
            self.empty.place_forget()
            self.clear_btn.state(["!disabled"])
        else:
            self.empty.place(relx=0.5, rely=0.4, anchor="center")
            self.empty.lift()  # the list was created later and would cover it
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
        tr = self.main.t
        if messagebox.askyesno(tr("hist_confirm_title"), tr("hist_confirm"), parent=self.win):
            self.app.clear_history()
