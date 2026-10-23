# Cambios

## [0.2.0] — 2026-10-23

- **Historial**: cada búsqueda se guarda con su fecha. Botón «Historial» (Ctrl+H) con la lista completa, y flechas ◀ ▶ (Alt+← / Alt+→) para ir a la búsqueda anterior o siguiente.
- **Menú «Opciones»** con todo lo que se enciende y apaga, recordado entre sesiones: vigilar portapapeles, mostrar la ventana al capturar, siempre visible, modo oscuro, significado en inglés y recordar el historial.
- **Modo oscuro**, incluida la barra de título de Windows. La primera vez sigue el tema de Windows.
- «Acerca de…» también desde el ícono de la bandeja.

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

[0.2.0]: https://github.com/kukolin/Yomitoru/releases/tag/v0.2.0
[0.1.0]: https://github.com/kukolin/Yomitoru/releases/tag/v0.1.0
