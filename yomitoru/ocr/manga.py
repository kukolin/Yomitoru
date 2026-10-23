"""Motor alternativo: manga-ocr (más preciso con texto japonés, pero pesado: PyTorch + ~450 MB de modelo).

Instalar con:  pip install manga-ocr   (descarga el modelo la primera vez; después funciona offline)
Usar con:      python -m yomitoru --ocr manga
"""

from __future__ import annotations

from PIL import Image

from . import OcrEngine, OcrUnavailableError


class MangaOcrEngine(OcrEngine):
    name = "manga"

    def __init__(self):
        self._model = None

    def check(self) -> None:
        if self._model is not None:
            return
        try:
            from manga_ocr import MangaOcr
        except ImportError as e:
            raise OcrUnavailableError("manga-ocr no está instalado. Ejecutá: pip install manga-ocr") from e
        self._model = MangaOcr()

    def recognize(self, image: Image.Image) -> str:
        self.check()
        return self._model(image.convert("RGB")).strip()
