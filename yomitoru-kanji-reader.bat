@echo off
rem Opens Yomitoru Kanji Reader without a console window.
cd /d "%~dp0"
start "" pythonw -m yomitoru %*
