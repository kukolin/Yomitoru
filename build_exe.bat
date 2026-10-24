@echo off
rem Builds dist\yomitoru-kanji-reader.exe (a single file with the dictionary bundled inside).
setlocal
cd /d "%~dp0"

python -m pip install --quiet -r requirements.txt pyinstaller || exit /b 1
rem creates (or updates, if it comes from an older version) data\kanjidic2.sqlite
python -m yomitoru.setup_dict || exit /b 1
python scripts\build_assets.py || exit /b 1

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name yomitoru-kanji-reader ^
    --icon build\yomitoru.ico ^
    --version-file build\version_info.txt ^
    --collect-all winrt ^
    --hidden-import pystray._win32 ^
    --add-data "data\kanjidic2.sqlite;data" ^
    run_yomitoru.py || exit /b 1

echo.
echo Done: dist\yomitoru-kanji-reader.exe
