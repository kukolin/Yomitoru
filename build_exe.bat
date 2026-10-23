@echo off
rem Empaqueta Yomitoru como dist\Yomitoru.exe (un solo archivo, con el diccionario adentro).
setlocal
cd /d "%~dp0"

python -m pip install --quiet -r requirements.txt pyinstaller || exit /b 1
if not exist data\kanjidic2.sqlite (
    python -m yomitoru.setup_dict || exit /b 1
)
python scripts\build_assets.py || exit /b 1

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name Yomitoru ^
    --icon build\yomitoru.ico ^
    --version-file build\version_info.txt ^
    --collect-all winrt ^
    --hidden-import pystray._win32 ^
    --add-data "data\kanjidic2.sqlite;data" ^
    run_yomitoru.py || exit /b 1

echo.
echo Listo: dist\Yomitoru.exe
