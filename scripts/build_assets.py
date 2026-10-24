"""Generate the .exe icon and version info in build/ (used by build_exe.bat)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from yomitoru import APP_NAME, AUTHOR, EXE_NAME, __version__  # noqa: E402
from yomitoru.tray import make_icon_image  # noqa: E402

VERSION_INFO = """VSVersionInfo(
  ffi=FixedFileInfo(filevers={tup}, prodvers={tup}, mask=0x3f, flags=0x0, OS=0x40004,
                    fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904b0', [
      StringStruct('CompanyName', '{author}'),
      StringStruct('FileDescription', '{app} - Lightweight, fast kanji lookup from screenshots'),
      StringStruct('FileVersion', '{ver}'),
      StringStruct('InternalName', '{app}'),
      StringStruct('LegalCopyright', '(c) 2026 {author}. MIT. KANJIDIC2 (c) EDRDG, CC BY-SA 4.0'),
      StringStruct('OriginalFilename', '{exe}.exe'),
      StringStruct('ProductName', '{app}'),
      StringStruct('ProductVersion', '{ver}')])]),
    VarFileInfo([VarStruct('Translation', [0x0409, 1200])])
  ]
)
"""


def main() -> None:
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    sizes = [(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]
    make_icon_image(256).save(out / "yomitoru.ico", sizes=sizes)
    parts = [int(p) for p in __version__.split(".")] + [0]
    tup = tuple(parts[:4])
    (out / "version_info.txt").write_text(
        VERSION_INFO.format(tup=tup, author=AUTHOR, app=APP_NAME, exe=EXE_NAME, ver=__version__), encoding="utf-8")
    print(f"build/yomitoru.ico and build/version_info.txt for {APP_NAME} {__version__}")


if __name__ == "__main__":
    main()
