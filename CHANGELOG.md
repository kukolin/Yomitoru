# Changelog

## [0.3.0] — 2026-10-24

- **New name: Yomitoru Kanji Reader.** The download is now `yomitoru-kanji-reader.exe`, and the repository moves to `kukolin/yomitoru-kanji-reader` (old links redirect).
- **10 languages**: English, español, 日本語, 中文（简体）, 한국어, français, português, Deutsch, italiano and русский, from **Options → Language**. Meanings are shown in French and Portuguese too, besides English and Spanish (what KANJIDIC2 includes); without a translation, the English meaning is shown with a note. The first time, the Windows language is used.
- Prominent **● Listening / ○ Off** indicator in the main window (it replaces "Watch clipboard" in the menu).
- **Search on jisho.org** looks up whatever is typed in the text field at that moment.
- Everything inside a kanji card can be **selected and copied** (Ctrl+C or right-click → Copy), and a **copy icon** under each kanji puts it straight on the clipboard.
- The status bar shows **Captured: today 19:42** (or **Searched:** if typed by hand) instead of "History: 2 of 2".
- History and About open centered over the main window.
- The history is always saved; it can be cleared from the history window.
- Removed the "Also show the meaning in English" and "Remember the history" options.
- Shorter "No kanji in the text." message.
- Smoother indicator dot, and the window adapts its minimum width to the language.
- The dictionary database format changed: one from an older version is rebuilt automatically on startup.
- README in English, Español, 日本語, 中文, 한국어, Português, Français and Deutsch.

## [0.2.0] — 2026-10-23

- **History**: every lookup is saved with its date. A "History" button (Ctrl+H) with the full list, and ◀ ▶ arrows (Alt+← / Alt+→) to go to the previous or next lookup.
- **Options menu** with everything that can be switched on and off, remembered between sessions.
- **Dark mode**, including the Windows title bar. The first time, it follows the Windows theme.
- "About…" also from the tray icon.

## [0.1.0] — 2026-10-23

First public version.

- Automatically detects Win+Shift+S screenshots in the clipboard.
- Offline Japanese OCR with the native Windows engine (`Windows.Media.Ocr`), with adaptive preprocessing and voting between variants so standalone kanji are recognized.
- For every kanji: on'yomi and kun'yomi in hiragana, meaning in Spanish (or English), strokes, JLPT and grade, and a jisho.org link.
- Editable recognized text with a button to search again.
- "Always on top" window, Esc to hide, tray icon to pause or resume.
- KANJIDIC2 dictionary (EDRDG, CC BY-SA 4.0) converted to SQLite.
- Optional alternative engine: manga-ocr.
- Portable Windows executable.

[0.3.0]: https://github.com/kukolin/yomitoru-kanji-reader/releases/tag/v0.3.0
[0.2.0]: https://github.com/kukolin/yomitoru-kanji-reader/releases/tag/v0.2.0
[0.1.0]: https://github.com/kukolin/yomitoru-kanji-reader/releases/tag/v0.1.0
