# Cambios

## [0.1.0] — 2026-10-23

Primera versión pública.

- Detecta automáticamente las capturas de Win+Shift+S en el portapapeles.
- OCR japonés offline con el motor nativo de Windows (`Windows.Media.Ocr`), con preprocesado adaptativo y votación entre variantes para reconocer kanji sueltos.
- Por cada kanji: lecturas on'yomi y kun'yomi en hiragana, significado en español (o inglés), trazos, JLPT y grado, y link a jisho.org.
- Link a la palabra completa en jisho.org cuando se reconoce más de un carácter.
- Texto reconocido editable, con botón para volver a buscar.
- Ventana con «Siempre visible», se esconde con Esc, ícono en la bandeja para pausar o reanudar la vigilancia.
- Diccionario KANJIDIC2 (EDRDG, CC BY-SA 4.0) convertido a SQLite.
- Motor alternativo opcional: manga-ocr.
- Ejecutable portable para Windows (`Yomitoru.exe`).

[0.1.0]: https://github.com/kukolin/Yomitoru/releases/tag/v0.1.0
