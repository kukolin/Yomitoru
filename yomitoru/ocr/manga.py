"""Alternative engine: manga-ocr (more accurate with Japanese text, but heavy: PyTorch + ~450 MB model).

Install:  pip install manga-ocr   (downloads the model the first time; works offline afterwards)
Use:      python -m yomitoru --ocr manga
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
            raise OcrUnavailableError("manga-ocr is not installed. Run: pip install manga-ocr") from e
        self._model = MangaOcr()

    def recognize(self, image: Image.Image) -> str:
        self.check()
        return self._model(image.convert("RGB")).strip()
