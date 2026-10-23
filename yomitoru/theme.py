"""Paletas claro/oscuro y su aplicación a ttk, menús y la barra de título de Windows."""

from __future__ import annotations

import ctypes
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk


@dataclass(frozen=True)
class Theme:
    dark: bool
    bg: str            # fondo de las ventanas
    card: str          # fondo de las tarjetas, campos y listas
    border: str
    fg: str
    muted: str
    link: str
    button: str
    button_hover: str
    button_pressed: str
    select: str


LIGHT = Theme(dark=False, bg="#f3f3f3", card="#ffffff", border="#d6d6d6", fg="#1b1b1b",
              muted="#6b6b6b", link="#1a6fd1", button="#fdfdfd", button_hover="#eaeaea",
              button_pressed="#dcdcdc", select="#cce4f7")
DARK = Theme(dark=True, bg="#1f1f1f", card="#2b2b2b", border="#404040", fg="#e6e6e6",
             muted="#9d9d9d", link="#6cb4ff", button="#2d2d2d", button_hover="#3a3a3a",
             button_pressed="#454545", select="#2f4f73")


def get_theme(dark: bool) -> Theme:
    return DARK if dark else LIGHT


def apply_ttk(style: ttk.Style, t: Theme, font, small_font, row_height: int) -> None:
    # "clam" es el tema de ttk que respeta todos los colores (el nativo de Windows no)
    style.theme_use("clam")
    style.configure(".", background=t.bg, foreground=t.fg, bordercolor=t.border, lightcolor=t.bg,
                    darkcolor=t.bg, troughcolor=t.bg, fieldbackground=t.card, focuscolor=t.border,
                    selectbackground=t.select, selectforeground=t.fg, insertcolor=t.fg, font=font)
    style.configure("TFrame", background=t.bg)
    style.configure("TLabel", background=t.bg, foreground=t.fg)
    style.configure("Muted.TLabel", foreground=t.muted, font=small_font)
    style.configure("TButton", background=t.button, foreground=t.fg, bordercolor=t.border,
                    lightcolor=t.button, darkcolor=t.button, padding=(10, 3), relief="flat")
    style.map("TButton",
              background=[("disabled", t.bg), ("pressed", t.button_pressed), ("active", t.button_hover)],
              foreground=[("disabled", t.muted)],
              bordercolor=[("disabled", t.border)],
              lightcolor=[("pressed", t.button_pressed), ("active", t.button_hover)],
              darkcolor=[("pressed", t.button_pressed), ("active", t.button_hover)])
    style.configure("Nav.TButton", padding=(6, 3), width=2)
    style.configure("TMenubutton", background=t.button, foreground=t.fg, bordercolor=t.border,
                    lightcolor=t.button, darkcolor=t.button, arrowcolor=t.fg, padding=(10, 3), relief="flat")
    style.map("TMenubutton", background=[("pressed", t.button_pressed), ("active", t.button_hover)],
              lightcolor=[("active", t.button_hover)], darkcolor=[("active", t.button_hover)])
    style.configure("TEntry", fieldbackground=t.card, foreground=t.fg, bordercolor=t.border,
                    lightcolor=t.card, darkcolor=t.card, insertcolor=t.fg, padding=(6, 2))
    style.map("TEntry", bordercolor=[("focus", t.link)], lightcolor=[("focus", t.card)])
    style.configure("Vertical.TScrollbar", background=t.button, troughcolor=t.bg, bordercolor=t.bg,
                    lightcolor=t.button, darkcolor=t.button, arrowcolor=t.muted, gripcount=0)
    style.map("Vertical.TScrollbar", background=[("active", t.button_hover)])
    style.configure("Treeview", background=t.card, fieldbackground=t.card, foreground=t.fg,
                    bordercolor=t.border, lightcolor=t.card, darkcolor=t.card, rowheight=row_height, font=font)
    style.map("Treeview", background=[("selected", t.select)], foreground=[("selected", t.fg)])
    style.configure("Treeview.Heading", background=t.bg, foreground=t.muted, bordercolor=t.border,
                    lightcolor=t.bg, darkcolor=t.bg, relief="flat", font=small_font)
    style.map("Treeview.Heading", background=[("active", t.button_hover)])


def style_menu(menu: tk.Menu, t: Theme) -> None:
    menu.configure(bg=t.card, fg=t.fg, activebackground=t.select, activeforeground=t.fg,
                   selectcolor=t.fg, disabledforeground=t.muted, relief="flat", borderwidth=1)


def set_titlebar(window: tk.Misc, dark: bool) -> None:
    """Barra de título oscura/clara en Windows 10 (20H1+) y 11."""
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
        # Windows no repinta el marco solo: SWP_FRAMECHANGED | NOMOVE | NOSIZE | NOZORDER | NOACTIVATE
        ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x20 | 0x2 | 0x1 | 0x4 | 0x10)
    except (AttributeError, OSError):
        pass
