"""Native Windows OCR (Windows.Media.Ocr) through pywinrt.

The Windows engine is very sensitive to the absolute text size and almost never
recognizes a standalone kanji. So instead of a single "scale up 2–3×":
  1. convert to grayscale, dark text on a light background, cropped to the content;
  2. scale so the line height lands on several target sizes (~20–40 px);
  3. try every size in "bold" too (thin fonts fail more often);
  4. if it looks like a single character, also try it repeated (日日日), which the
     engine does recognize;
  5. drop results with more lines than the image has (the engine sometimes splits a
     kanji like 語 into two "lines") and pick the most voted result.
"""

from __future__ import annotations

import asyncio
import io
import re
from collections import Counter

from PIL import Image, ImageFilter, ImageOps

from . import OcrEngine, OcrUnavailableError

LANGUAGE_MISSING = "Windows Japanese OCR is not installed (Settings > Time & language > Language)."

TARGET_HEIGHTS = (20, 26, 32, 40)
TILE_HEIGHTS = (20, 28, 40)
TILE_COUNT = 3
INK_THRESHOLD = 160  # after autocontrast, darker than this is "ink"

_CJK = "　-ヿ㐀-䶿一-鿿豈-﫿＀-￯"
_SPACE_BETWEEN_CJK = re.compile(rf"(?<=[{_CJK}])\s+(?=[{_CJK}])")
_JAPANESE_CHAR = re.compile(rf"[{_CJK}]")


def clean_text(text: str) -> str:
    """Windows OCR separates every Japanese character with spaces: remove them."""
    return _SPACE_BETWEEN_CJK.sub("", text).strip()


def normalize(image: Image.Image) -> Image.Image:
    """Grayscale, dark text on light, cropped to the content."""
    gray = ImageOps.autocontrast(ImageOps.grayscale(image))
    w, h = gray.width - 1, gray.height - 1
    corners = sorted(gray.getpixel(p) for p in ((0, 0), (w, 0), (0, h), (w, h)))
    if (corners[1] + corners[2]) / 2 < 128:  # fondo oscuro
        gray = ImageOps.invert(gray)
    ink = gray.point(lambda v: 255 if v < INK_THRESHOLD else 0)
    bbox = ink.getbbox()
    return gray.crop(bbox) if bbox else gray


def line_metrics(gray: Image.Image) -> tuple[int, int]:
    """(line height, number of lines) estimated from the horizontal ink profile."""
    data = gray.point(lambda v: 1 if v < INK_THRESHOLD else 0).tobytes()
    w = gray.width
    rows = [any(data[y * w:(y + 1) * w]) for y in range(gray.height)]
    runs, start = [], None
    for y, has_ink in enumerate(rows + [False]):
        if has_ink and start is None:
            start = y
        elif not has_ink and start is not None:
            runs.append([start, y])
            start = None
    # merge small gaps (separate strokes within the same character)
    merged: list[list[int]] = []
    for run in runs:
        if merged and run[0] - merged[-1][1] < 0.1 * gray.height + 2:
            merged[-1][1] = run[1]
        else:
            merged.append(run)
    tallest = max((b - a for a, b in merged), default=gray.height)
    lines = [b - a for a, b in merged if b - a >= 0.5 * tallest]
    if not lines:
        return gray.height, 1
    return max(1, round(sum(lines) / len(lines))), len(lines)


def _scaled(gray: Image.Image, factor: float) -> Image.Image:
    size = (max(1, round(gray.width * factor)), max(1, round(gray.height * factor)))
    return gray.resize(size, Image.LANCZOS)


def _pad(gray: Image.Image, pad: int) -> Image.Image:
    return ImageOps.expand(gray, border=pad, fill=255)


def _tiled(gray: Image.Image, count: int, gap: int, pad: int) -> Image.Image:
    canvas = Image.new("L", (count * gray.width + (count - 1) * gap + 2 * pad, gray.height + 2 * pad), 255)
    for i in range(count):
        canvas.paste(gray, (pad + i * (gray.width + gap), pad))
    return canvas


def variants(image: Image.Image, max_dim: int = 10000) -> list[tuple[str, Image.Image, int]]:
    """Images to recognize: (kind, image, maximum acceptable number of lines).

    Kind "line": the scaled image; "tile": the character repeated TILE_COUNT times.
    """
    gray = normalize(image)
    lh, n_lines = line_metrics(gray)
    # if the estimate suggests several lines, also try it as a single one
    # (the strokes of 三 or 二 look like lines)
    heights = {lh, gray.height} if lh < 0.7 * gray.height else {gray.height}
    out: list[tuple[str, Image.Image, int]] = []
    for h in sorted(heights):
        max_lines = n_lines if h == lh else 1
        for target in TARGET_HEIGHTS:
            factor = min(target / h, max_dim / (max(gray.size) + target))
            scaled = _scaled(gray, factor)
            out.append(("line", _pad(scaled, target // 2), max_lines))
            out.append(("line", _pad(scaled.filter(ImageFilter.MinFilter(3)), target // 2), max_lines))
    # a single character? (roughly square; if not, _untile discards the result)
    if gray.width <= 1.5 * gray.height:
        for target in TILE_HEIGHTS:
            small = _scaled(gray, target / gray.height)
            out.append(("tile", _tiled(small, TILE_COUNT, round(target * 0.15), target // 2), 1))
    return out


def _untile(text: str) -> str:
    """'日日日' -> '日'. If it is not a clear repetition, the result is discarded."""
    chars = [c for c in text if _JAPANESE_CHAR.match(c)]
    if len(chars) < 2:
        return ""
    char, n = Counter(chars).most_common(1)[0]
    return char if n >= 2 and n >= len(chars) - 1 else ""


def choose(results: list[str]) -> str:
    """Pick the most voted text; ties are broken by share of Japanese characters and length."""
    votes = Counter(r for r in results if r)
    if not votes:
        return ""

    def score(text: str):
        jp = len(_JAPANESE_CHAR.findall(text))
        return votes[text], jp / max(1, len(text.replace("\n", ""))), -text.count("\n"), jp

    return max(votes, key=score)


class WindowsOcr(OcrEngine):
    name = "windows"

    def __init__(self, language: str = "ja"):
        self.language = language
        self._engine = None

    def check(self) -> None:
        try:
            from winrt.windows.globalization import Language
            from winrt.windows.media.ocr import OcrEngine as WinOcrEngine
        except ImportError as e:  # pragma: no cover
            raise OcrUnavailableError(
                f"Missing pywinrt packages ({e.name}). Run: pip install -r requirements.txt"
            ) from e
        lang = Language(self.language)
        if not WinOcrEngine.is_language_supported(lang):
            raise OcrUnavailableError(LANGUAGE_MISSING, code="language_missing")
        self._engine = WinOcrEngine.try_create_from_language(lang)
        if self._engine is None:
            raise OcrUnavailableError(LANGUAGE_MISSING, code="language_missing")

    def recognize(self, image: Image.Image) -> str:
        if self._engine is None:
            self.check()
        from winrt.windows.media.ocr import OcrEngine as WinOcrEngine
        return asyncio.run(self._recognize_variants(image, WinOcrEngine.max_image_dimension))

    async def _recognize_variants(self, image: Image.Image, max_dim: int) -> str:
        results = []
        for kind, img, max_lines in variants(image, max_dim):
            text = await self._recognize_one(img)
            if text.count("\n") + 1 > max_lines:
                continue
            results.append(_untile(text) if kind == "tile" else text)
        return choose(results)

    async def _recognize_one(self, image: Image.Image) -> str:
        from winrt.windows.graphics.imaging import BitmapDecoder
        from winrt.windows.storage.streams import DataWriter, InMemoryRandomAccessStream

        png = io.BytesIO()
        image.save(png, format="PNG")
        stream = InMemoryRandomAccessStream()
        writer = DataWriter(stream)
        writer.write_bytes(png.getvalue())
        await writer.store_async()
        writer.detach_stream()
        stream.seek(0)
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        result = await self._engine.recognize_async(bitmap)
        return "\n".join(clean_text(line.text) for line in result.lines if line.text.strip())
