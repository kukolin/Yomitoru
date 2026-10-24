"""Detection of new images in the clipboard."""

from __future__ import annotations

import ctypes
import hashlib

from PIL import Image, ImageGrab


def _sequence_number() -> int | None:
    """Counter Windows increments on every clipboard change (free to query)."""
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
    """Call `poll()` periodically: it returns the image only when it is new."""

    def __init__(self, grab=ImageGrab.grabclipboard, sequence=_sequence_number):
        self._grab = grab
        self._sequence = sequence
        self._last_seq: int | None = None
        self._last_hash: str | None = None

    def prime(self) -> None:
        """Mark the current image as seen (so an old screenshot is not processed at startup)."""
        self._last_seq = None
        self.poll()

    def poll(self) -> Image.Image | None:
        seq = self._sequence()
        if seq is not None and seq == self._last_seq:
            return None
        self._last_seq = seq
        try:
            content = self._grab()
        except OSError:  # clipboard busy in another application: retry next cycle
            self._last_seq = None
            return None
        if not isinstance(content, Image.Image):  # text, file list or empty
            return None
        digest = image_hash(content)
        if digest == self._last_hash:
            return None
        self._last_hash = digest
        return content
