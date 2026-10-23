"""OCR nativo de Windows (Windows.Media.Ocr) vía pywinrt.

El motor de Windows es muy sensible al tamaño absoluto del texto y casi nunca
reconoce un kanji suelto. Por eso, en vez de un único "agrandar 2–3×":
  1. se pasa a escala de grises, texto oscuro sobre fondo claro, recortado al contenido;
  2. se escala para que la altura de línea quede en varios tamaños objetivo (~20–40 px);
  3. cada tamaño se prueba también en "negrita" (las fuentes finas fallan más);
  4. si parece un solo carácter, además se prueba repitiéndolo (日日日), lo que el
     motor sí reconoce;
  5. se descartan resultados con más líneas de las que tiene la imagen (el motor
     a veces parte un kanji como 語 en dos "líneas") y se elige el más votado.
"""

from __future__ import annotations

import asyncio
import io
import re
from collections import Counter

from PIL import Image, ImageFilter, ImageOps

from . import OcrEngine, OcrUnavailableError

INSTALL_HELP = (
    "El OCR japonés de Windows no está instalado.\n\n"
    "Para instalarlo:\n"
    "  1. Abrí Configuración → Hora e idioma → Idioma y región.\n"
    "  2. En «Idiomas preferidos», hacé clic en «Agregar un idioma».\n"
    "  3. Buscá «Japonés» (日本語) y seleccionalo.\n"
    "  4. Asegurate de que la opción «Reconocimiento óptico de caracteres (OCR)» "
    "esté marcada (las demás son opcionales) e instalá.\n"
    "  5. Reiniciá Yomitoru.\n\n"
    "No hace falta cambiar el idioma de Windows."
)

TARGET_HEIGHTS = (20, 26, 32, 40)
TILE_HEIGHTS = (20, 28, 40)
TILE_COUNT = 3
INK_THRESHOLD = 160  # tras autocontraste, más oscuro que esto es "tinta"

_CJK = "　-ヿ㐀-䶿一-鿿豈-﫿＀-￯"
_SPACE_BETWEEN_CJK = re.compile(rf"(?<=[{_CJK}])\s+(?=[{_CJK}])")
_JAPANESE_CHAR = re.compile(rf"[{_CJK}]")


def clean_text(text: str) -> str:
    """El OCR de Windows separa cada carácter japonés con espacios: se quitan."""
    return _SPACE_BETWEEN_CJK.sub("", text).strip()


def normalize(image: Image.Image) -> Image.Image:
    """Escala de grises, texto oscuro sobre claro, recortado al contenido."""
    gray = ImageOps.autocontrast(ImageOps.grayscale(image))
    w, h = gray.width - 1, gray.height - 1
    corners = sorted(gray.getpixel(p) for p in ((0, 0), (w, 0), (0, h), (w, h)))
    if (corners[1] + corners[2]) / 2 < 128:  # fondo oscuro
        gray = ImageOps.invert(gray)
    ink = gray.point(lambda v: 255 if v < INK_THRESHOLD else 0)
    bbox = ink.getbbox()
    return gray.crop(bbox) if bbox else gray


def line_metrics(gray: Image.Image) -> tuple[int, int]:
    """(altura de línea, cantidad de líneas) estimadas con el perfil horizontal de tinta."""
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
    # unir huecos chicos (trazos separados dentro de un mismo carácter)
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
    """Imágenes a reconocer: (tipo, imagen, máximo de líneas aceptable).

    Tipo "line": la imagen escalada; "tile": el carácter repetido TILE_COUNT veces.
    """
    gray = normalize(image)
    lh, n_lines = line_metrics(gray)
    # si la estimación sugiere varias líneas, probar también como una sola
    # (los trazos de 三 o 二 se confunden con líneas)
    heights = {lh, gray.height} if lh < 0.7 * gray.height else {gray.height}
    out: list[tuple[str, Image.Image, int]] = []
    for h in sorted(heights):
        max_lines = n_lines if h == lh else 1
        for target in TARGET_HEIGHTS:
            factor = min(target / h, max_dim / (max(gray.size) + target))
            scaled = _scaled(gray, factor)
            out.append(("line", _pad(scaled, target // 2), max_lines))
            out.append(("line", _pad(scaled.filter(ImageFilter.MinFilter(3)), target // 2), max_lines))
    # ¿un solo carácter? (aproximadamente cuadrado; si no lo es, _untile descarta el resultado)
    if gray.width <= 1.5 * gray.height:
        for target in TILE_HEIGHTS:
            small = _scaled(gray, target / gray.height)
            out.append(("tile", _tiled(small, TILE_COUNT, round(target * 0.15), target // 2), 1))
    return out


def _untile(text: str) -> str:
    """'日日日' -> '日'. Si no es una repetición clara, descarta el resultado."""
    chars = [c for c in text if _JAPANESE_CHAR.match(c)]
    if len(chars) < 2:
        return ""
    char, n = Counter(chars).most_common(1)[0]
    return char if n >= 2 and n >= len(chars) - 1 else ""


def choose(results: list[str]) -> str:
    """Elige el texto más votado; desempata por proporción de caracteres japoneses y largo."""
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
                f"Faltan los paquetes de pywinrt ({e.name}). Ejecutá: pip install -r requirements.txt"
            ) from e
        lang = Language(self.language)
        if not WinOcrEngine.is_language_supported(lang):
            raise OcrUnavailableError(INSTALL_HELP)
        self._engine = WinOcrEngine.try_create_from_language(lang)
        if self._engine is None:
            raise OcrUnavailableError(INSTALL_HELP)

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
