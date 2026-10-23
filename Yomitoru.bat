@echo off
rem Abre Yomitoru sin ventana de consola.
cd /d "%~dp0"
start "" pythonw -m yomitoru %*
