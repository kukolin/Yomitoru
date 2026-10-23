from PIL import Image

from yomitoru.clipboard import ClipboardWatcher
from yomitoru.dictionary import KanjiInfo
from yomitoru.lookup import jisho_kanji_url, jisho_word_url, lookup_text


class FakeDict:
    def lookup(self, literal):
        return KanjiInfo(literal, onyomi=["にち"]) if literal == "日" else None


def test_urls():
    assert jisho_kanji_url("日") == "https://jisho.org/search/%E6%97%A5%23kanji"
    assert jisho_word_url("日本語") == "https://jisho.org/search/%E6%97%A5%E6%9C%AC%E8%AA%9E"


def test_lookup_text_multiple_chars():
    res = lookup_text("日本 を\n日", FakeDict())
    assert res.text == "日本を日"
    assert [e.literal for e in res.kanji] == ["日", "本"]
    assert res.kanji[0].info.onyomi == ["にち"]
    assert res.kanji[1].info is None
    assert res.word_url == jisho_word_url("日本を日")


def test_lookup_text_single_kanji_has_no_word_link():
    res = lookup_text("日", FakeDict())
    assert res.word_url is None and len(res.kanji) == 1


def test_lookup_text_only_kana():
    res = lookup_text("ありがとう", FakeDict())
    assert res.kanji == [] and res.word_url is not None


class FakeClipboard:
    def __init__(self):
        self.content, self.seq = None, 0

    def set(self, content):
        self.content = content
        self.seq += 1


def test_watcher_only_new_images():
    cb = FakeClipboard()
    w = ClipboardWatcher(grab=lambda: cb.content, sequence=lambda: cb.seq)
    cb.set(Image.new("RGB", (10, 10), "red"))
    w.prime()
    assert w.poll() is None  # la imagen que ya estaba al iniciar se ignora

    blue = Image.new("RGB", (10, 10), "blue")
    cb.set(blue)
    assert w.poll() is blue
    assert w.poll() is None  # sin cambios

    cb.set("texto copiado")
    assert w.poll() is None
    cb.set(Image.new("RGB", (10, 10), "blue"))  # misma imagen otra vez: mismo hash
    assert w.poll() is None
    cb.set(Image.new("RGB", (10, 10), "green"))
    assert w.poll() is not None


def test_watcher_clipboard_busy():
    cb = FakeClipboard()

    def grab():
        raise OSError("busy")

    w = ClipboardWatcher(grab=grab, sequence=lambda: cb.seq)
    assert w.poll() is None
