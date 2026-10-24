"""Launcher (used by PyInstaller, which needs a script rather than `-m package`)."""

import sys

from yomitoru.app import main

if __name__ == "__main__":
    sys.exit(main())
