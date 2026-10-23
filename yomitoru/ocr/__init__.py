"""Interfaz de OCR intercambiable.

Cada motor implementa `OcrEngine.recognize(image) -> str`. Para agregar otro motor,
crear una subclase y registrarla en `create_engine`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image


class OcrUnavailableError(RuntimeError):
    """El motor no se puede usar (falta el idioma, una dependencia, etc.). El mensaje es para el usuario."""


class OcrEngine(ABC):
    name = "base"

    @abstractmethod
    def recognize(self, image: Image.Image) -> str:
        """Devuelve el texto japonés reconocido (sin espacios entre caracteres)."""

    def check(self) -> None:
        """Lanza OcrUnavailableError si el motor no está listo para usarse."""


def create_engine(name: str = "windows") -> OcrEngine:
    if name == "windows":
        from .windows_ocr import WindowsOcr
        return WindowsOcr()
    if name == "manga":
        from .manga import MangaOcrEngine
        return MangaOcrEngine()
    raise ValueError(f"Motor de OCR desconocido: {name!r} (opciones: windows, manga)")
