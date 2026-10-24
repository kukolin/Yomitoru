"""Swappable OCR interface.

Each engine implements `OcrEngine.recognize(image) -> str`. To add an engine,
create a subclass and register it in `create_engine`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image


class OcrUnavailableError(RuntimeError):
    """The engine cannot be used (missing language, dependency, etc.).

    `code` identifies known causes so the UI can show translated help
    ("language_missing": the Windows Japanese OCR is not installed).
    """

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code


class OcrEngine(ABC):
    name = "base"

    @abstractmethod
    def recognize(self, image: Image.Image) -> str:
        """Return the recognized Japanese text (without spaces between characters)."""

    def check(self) -> None:
        """Raise OcrUnavailableError if the engine is not ready to be used."""


def create_engine(name: str = "windows") -> OcrEngine:
    if name == "windows":
        from .windows_ocr import WindowsOcr
        return WindowsOcr()
    if name == "manga":
        from .manga import MangaOcrEngine
        return MangaOcrEngine()
    raise ValueError(f"Unknown OCR engine: {name!r} (options: windows, manga)")
