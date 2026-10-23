"""Detección de imágenes nuevas en el portapapeles."""

from __future__ import annotations

import ctypes
import hashlib

from PIL import Image, ImageGrab


def _sequence_number() -> int | None:
    """Contador que Windows incrementa con cada cambio del portapapeles (consultarlo es gratis)."""
    try:
        return ctypes.windll.user32.GetClipboardSequenceNumber()
    except (AttributeError, OSError):
        return None


def image_hash(image: Image.Image) -> str:
    h = hashlib.blake2b(digest_size=16)
    h.update(f"{image.mode}{image.size}".encode())
    h.update(image.tobytes())
    return h.hexdigest()


class ClipboardWatcher:
    """Llamar a `poll()` periódicamente: devuelve la imagen solo si es nueva."""

    def __init__(self, grab=ImageGrab.grabclipboard, sequence=_sequence_number):
        self._grab = grab
        self._sequence = sequence
        self._last_seq: int | None = None
        self._last_hash: str | None = None

    def prime(self) -> None:
        """Marca como vista la imagen actual (para no procesar una captura vieja al iniciar)."""
        self._last_seq = None
        self.poll()

    def poll(self) -> Image.Image | None:
        seq = self._sequence()
        if seq is not None and seq == self._last_seq:
            return None
        self._last_seq = seq
        try:
            content = self._grab()
        except OSError:  # portapapeles ocupado por otra aplicación: reintentar en el próximo ciclo
            self._last_seq = None
            return None
        if not isinstance(content, Image.Image):  # texto, lista de archivos o vacío
            return None
        digest = image_hash(content)
        if digest == self._last_hash:
            return None
        self._last_hash = digest
        return content
