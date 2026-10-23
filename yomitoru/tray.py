"""Ícono opcional en la bandeja del sistema (pystray). Si pystray no está, la app funciona igual."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw, ImageFont


def make_icon_image(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=size // 5, fill=(196, 40, 40, 255))
    for name in ("YuGothB.ttc", "meiryob.ttc", "msgothic.ttc"):
        try:
            font = ImageFont.truetype(name, int(size * 0.72))
            break
        except OSError:
            font = None
    if font:
        draw.text((size / 2, size / 2), "読", font=font, fill="white", anchor="mm")
    return img


class Tray:
    def __init__(self, on_show: Callable[[], None], on_toggle: Callable[[], None],
                 is_watching: Callable[[], bool], on_about: Callable[[], None], on_quit: Callable[[], None]):
        import pystray

        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", lambda: on_show(), default=True),
            pystray.MenuItem("Vigilar portapapeles", lambda: on_toggle(), checked=lambda item: is_watching()),
            pystray.MenuItem("Acerca de…", lambda: on_about()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", lambda: on_quit()),
        )
        self.icon = pystray.Icon("yomitoru", make_icon_image(), "Yomitoru 読み取る", menu)

    def start(self) -> None:
        self.icon.run_detached()

    def refresh(self) -> None:
        self.icon.update_menu()

    def stop(self) -> None:
        self.icon.stop()


def create_tray(**callbacks) -> Tray | None:
    try:
        tray = Tray(**callbacks)
        tray.start()
        return tray
    except Exception:  # sin pystray o sin soporte de bandeja: seguir sin ícono
        return None
