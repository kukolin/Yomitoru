"""Lanzador (usado por PyInstaller, que necesita un script y no un `-m paquete`)."""

import sys

from yomitoru.app import main

if __name__ == "__main__":
    sys.exit(main())
