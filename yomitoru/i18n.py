"""User interface languages.

To add a language: add it to LANGUAGES and add its dictionary to STRINGS with the same
keys as "en" (test_i18n checks that none is missing). Anything missing is shown in English.
"""

from __future__ import annotations

from datetime import datetime

# code -> name in that language, in menu order
LANGUAGES = {
    "en": "English",
    "es": "Español",
    "ja": "日本語",
    "zh": "中文（简体）",
    "ko": "한국어",
    "fr": "Français",
    "pt": "Português",
    "de": "Deutsch",
    "it": "Italiano",
    "ru": "Русский",
}
DEFAULT_LANGUAGE = "en"


STRINGS: dict[str, dict[str, str]] = {
    "es": {
        "listening": "Escuchando",
        "off": "Apagado",
        "history": "Historial",
        "options": "Opciones",
        "about_btn": "Acerca de…",
        "search_btn": "Buscar",
        "search_jisho": "Buscar en jisho.org",
        "view_jisho": "Ver en jisho.org",
        "copy": "Copiar",
        "copied": "Copiado: {text}",
        "copy_kanji": "Copiar el kanji",
        "no_text": "No se reconoció texto. Escribilo arriba y presioná Buscar.",
        "no_kanji": "No hay kanji en el texto.",
        "on": "On",
        "kun": "Kun",
        "meaning": "Significado",
        "meaning_in_english": "(en inglés)",
        "not_in_dict": "No está en KANJIDIC2",
        "strokes": "{n} trazos",
        "jlpt": "JLPT {n} (antiguo)",
        "grade": "grado {n}",
        "waiting": "Esperando una captura (Win+Shift+S)…",
        "paused": "Apagado: las capturas no se procesan.",
        "recognizing": "Reconociendo…",
        "captured_at": "Capturado: {when}",
        "searched_at": "Buscado: {when}",
        "history_cleared": "Historial borrado.",
        "ocr_error": "Error de OCR: {error}",
        "capture_no_ocr": "Captura recibida, pero el OCR no está disponible.",
        "ocr_status_unavailable": "OCR no disponible: podés escribir el texto a mano y presionar Buscar.",
        "ocr_title": "{app}: OCR no disponible",
        "ocr_install_help": (
            "El OCR japonés de Windows no está instalado.\n\n"
            "Para instalarlo:\n"
            "  1. Abrí Configuración → Hora e idioma → Idioma y región.\n"
            "  2. En «Idiomas preferidos», hacé clic en «Agregar un idioma».\n"
            "  3. Buscá «Japonés» (日本語) y seleccionalo.\n"
            "  4. Asegurate de que la opción «Reconocimiento óptico de caracteres (OCR)» "
            "esté marcada (las demás son opcionales) e instalá.\n"
            "  5. Reiniciá Yomitoru Kanji Reader.\n\n"
            "No hace falta cambiar el idioma de Windows."
        ),
        "opt_bring_to_front": "Mostrar la ventana al capturar",
        "opt_open_jisho": "Abrir jisho.org directamente al capturar",
        "opened_jisho": "Abierto en jisho.org: {text}",
        "opt_always_on_top": "Siempre visible",
        "opt_dark_mode": "Modo oscuro",
        "opt_language": "Idioma",
        "today": "hoy {time}",
        "yesterday": "ayer {time}",
        "date_fmt": "%d/%m %H:%M",
        "date_year_fmt": "%d/%m/%Y %H:%M",
        "hist_title": "Historial",
        "hist_col_text": "Texto",
        "hist_col_when": "Fecha",
        "hist_open": "Abrir",
        "hist_clear": "Borrar historial…",
        "hist_empty": "Todavía no hay búsquedas.\nCapturá un kanji con Win+Shift+S.",
        "hist_confirm_title": "Borrar historial",
        "hist_confirm": "¿Borrar todas las búsquedas del historial?",
        "about_title": "Acerca de {app}",
        "about_version": "Versión {version}",
        "about_tagline": "Capturá un kanji con Win+Shift+S y mirá al instante sus lecturas y su significado. "
                         "Funciona sin conexión: el OCR es el de Windows y el diccionario viene incluido.",
        "about_author": "Autor",
        "about_created_by": "Creado por {author}.",
        "about_source": "Código fuente",
        "about_releases": "Nuevas versiones",
        "about_report": "Reportar un error",
        "about_dictionary": "Diccionario",
        "about_dict_text": "Este programa usa el archivo KANJIDIC2 (versión {version}), propiedad del "
                           "Electronic Dictionary Research and Development Group (EDRDG), y se usa de acuerdo "
                           "con su licencia: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0).",
        "about_kanjidic": "Proyecto KANJIDIC",
        "about_edrdg": "Licencia del EDRDG",
        "about_license": "Licencia y créditos",
        "about_code_license": "Código bajo licencia MIT © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft) vía pywinrt. Interfaz: Tkinter, Pillow y pystray. "
                         "Los links abren Jisho.org.",
        "close": "Cerrar",
        "tray_show": "Mostrar",
        "tray_listen": "Escuchar el portapapeles",
        "tray_quit": "Salir",
        "already_running": "Yomitoru Kanji Reader ya está abierto (buscalo en la bandeja del sistema).",
        "dict_missing": "Falta el diccionario KANJIDIC2 (data/kanjidic2.sqlite).\n\n"
                        "¿Descargarlo ahora? (≈1,5 MB, solo esta vez)\n\n"
                        "También podés generarlo con:  python -m yomitoru.setup_dict",
        "dict_failed": "No se pudo preparar el diccionario KANJIDIC2:\n{error}",
    },
    "en": {
        "listening": "Listening",
        "off": "Off",
        "history": "History",
        "options": "Options",
        "about_btn": "About…",
        "search_btn": "Search",
        "search_jisho": "Search on jisho.org",
        "view_jisho": "View on jisho.org",
        "copy": "Copy",
        "copied": "Copied: {text}",
        "copy_kanji": "Copy the kanji",
        "no_text": "No text recognized. Type it above and press Search.",
        "no_kanji": "No kanji in the text.",
        "on": "On",
        "kun": "Kun",
        "meaning": "Meaning",
        "meaning_in_english": "",
        "not_in_dict": "Not in KANJIDIC2",
        "strokes": "{n} strokes",
        "jlpt": "JLPT {n} (old)",
        "grade": "grade {n}",
        "waiting": "Waiting for a screenshot (Win+Shift+S)…",
        "paused": "Off: screenshots are ignored.",
        "recognizing": "Recognizing…",
        "captured_at": "Captured: {when}",
        "searched_at": "Searched: {when}",
        "history_cleared": "History cleared.",
        "ocr_error": "OCR error: {error}",
        "capture_no_ocr": "Screenshot received, but OCR is not available.",
        "ocr_status_unavailable": "OCR not available: you can type the text and press Search.",
        "ocr_title": "{app}: OCR not available",
        "ocr_install_help": (
            "Windows' Japanese OCR is not installed.\n\n"
            "To install it:\n"
            "  1. Open Settings → Time & language → Language & region.\n"
            "  2. Under “Preferred languages”, click “Add a language”.\n"
            "  3. Search for “Japanese” (日本語) and select it.\n"
            "  4. Make sure “Optical character recognition (OCR)” is checked "
            "(the other options are optional) and install.\n"
            "  5. Restart Yomitoru Kanji Reader.\n\n"
            "You don't need to change your Windows display language."
        ),
        "opt_bring_to_front": "Show the window on capture",
        "opt_open_jisho": "Open jisho.org directly on capture",
        "opened_jisho": "Opened on jisho.org: {text}",
        "opt_always_on_top": "Always on top",
        "opt_dark_mode": "Dark mode",
        "opt_language": "Language",
        "today": "today {time}",
        "yesterday": "yesterday {time}",
        "date_fmt": "%b %d %H:%M",
        "date_year_fmt": "%b %d, %Y %H:%M",
        "hist_title": "History",
        "hist_col_text": "Text",
        "hist_col_when": "Date",
        "hist_open": "Open",
        "hist_clear": "Clear history…",
        "hist_empty": "No searches yet.\nCapture a kanji with Win+Shift+S.",
        "hist_confirm_title": "Clear history",
        "hist_confirm": "Delete all searches from the history?",
        "about_title": "About {app}",
        "about_version": "Version {version}",
        "about_tagline": "Capture a kanji with Win+Shift+S and instantly see its readings and meaning. "
                         "Works offline: OCR is built into Windows and the dictionary is included.",
        "about_author": "Author",
        "about_created_by": "Created by {author}.",
        "about_source": "Source code",
        "about_releases": "New versions",
        "about_report": "Report a bug",
        "about_dictionary": "Dictionary",
        "about_dict_text": "This program uses the KANJIDIC2 file (version {version}), which is the property of "
                           "the Electronic Dictionary Research and Development Group (EDRDG), and is used in "
                           "conformance with the Group's licence: Creative Commons Attribution-ShareAlike 4.0 "
                           "(CC BY-SA 4.0).",
        "about_kanjidic": "KANJIDIC project",
        "about_edrdg": "EDRDG licence",
        "about_license": "License and credits",
        "about_code_license": "Code under the MIT license © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft) via pywinrt. Interface: Tkinter, Pillow and pystray. "
                         "Links open Jisho.org.",
        "close": "Close",
        "tray_show": "Show",
        "tray_listen": "Listen to the clipboard",
        "tray_quit": "Quit",
        "already_running": "Yomitoru Kanji Reader is already running (look for it in the system tray).",
        "dict_missing": "The KANJIDIC2 dictionary is missing (data/kanjidic2.sqlite).\n\n"
                        "Download it now? (≈1.5 MB, only once)\n\n"
                        "You can also generate it with:  python -m yomitoru.setup_dict",
        "dict_failed": "Could not prepare the KANJIDIC2 dictionary:\n{error}",
    },
    "ja": {
        "listening": "監視中",
        "off": "停止中",
        "history": "履歴",
        "options": "オプション",
        "about_btn": "情報…",
        "search_btn": "検索",
        "search_jisho": "jisho.org で検索",
        "view_jisho": "jisho.org で見る",
        "copy": "コピー",
        "copied": "コピーしました: {text}",
        "copy_kanji": "漢字をコピー",
        "no_text": "文字を認識できませんでした。上に入力して「検索」を押してください。",
        "no_kanji": "テキストに漢字がありません。",
        "on": "音読み",
        "kun": "訓読み",
        "meaning": "意味",
        "meaning_in_english": "（英語）",
        "not_in_dict": "KANJIDIC2 にありません",
        "strokes": "{n}画",
        "jlpt": "旧JLPT {n}級",
        "grade": "学年 {n}",
        "waiting": "スクリーンショットを待っています (Win+Shift+S)…",
        "paused": "停止中：スクリーンショットは処理されません。",
        "recognizing": "認識中…",
        "captured_at": "キャプチャ: {when}",
        "searched_at": "検索: {when}",
        "history_cleared": "履歴を削除しました。",
        "ocr_error": "OCR エラー: {error}",
        "capture_no_ocr": "スクリーンショットを受け取りましたが、OCR を使用できません。",
        "ocr_status_unavailable": "OCR を使用できません。文字を入力して「検索」を押してください。",
        "ocr_title": "{app}: OCR を使用できません",
        "ocr_install_help": (
            "Windows の日本語 OCR がインストールされていません。\n\n"
            "インストール方法:\n"
            "  1. [設定] → [時刻と言語] → [言語と地域] を開きます。\n"
            "  2. [優先する言語] の [言語の追加] をクリックします。\n"
            "  3. 「日本語」を検索して選択します。\n"
            "  4. [光学式文字認識 (OCR)] にチェックが入っていることを確認して"
            "インストールします（ほかの機能は任意です）。\n"
            "  5. Yomitoru Kanji Reader を再起動します。"
        ),
        "opt_bring_to_front": "キャプチャ時にウィンドウを表示",
        "opt_open_jisho": "キャプチャ時に jisho.org を直接開く",
        "opened_jisho": "jisho.org で開きました: {text}",
        "opt_always_on_top": "常に手前に表示",
        "opt_dark_mode": "ダークモード",
        "opt_language": "言語",
        "today": "今日 {time}",
        "yesterday": "昨日 {time}",
        "date_fmt": "%m/%d %H:%M",
        "date_year_fmt": "%Y/%m/%d %H:%M",
        "hist_title": "履歴",
        "hist_col_text": "テキスト",
        "hist_col_when": "日時",
        "hist_open": "開く",
        "hist_clear": "履歴を削除…",
        "hist_empty": "まだ検索履歴がありません。\nWin+Shift+S で漢字をキャプチャしてください。",
        "hist_confirm_title": "履歴を削除",
        "hist_confirm": "履歴をすべて削除しますか？",
        "about_title": "{app} について",
        "about_version": "バージョン {version}",
        "about_tagline": "Win+Shift+S で漢字をキャプチャすると、読み方と意味がすぐに表示されます。"
                         "オフラインで動作します（OCR は Windows 標準、辞書は同梱）。",
        "about_author": "作者",
        "about_created_by": "作者: {author}",
        "about_source": "ソースコード",
        "about_releases": "新しいバージョン",
        "about_report": "不具合を報告",
        "about_dictionary": "辞書",
        "about_dict_text": "このプログラムは、Electronic Dictionary Research and Development Group (EDRDG) "
                           "が所有する KANJIDIC2 ファイル（バージョン {version}）を、同グループのライセンス "
                           "Creative Commons 表示 - 継承 4.0 (CC BY-SA 4.0) に従って使用しています。",
        "about_kanjidic": "KANJIDIC プロジェクト",
        "about_edrdg": "EDRDG ライセンス",
        "about_license": "ライセンスとクレジット",
        "about_code_license": "コードは MIT ライセンス © 2026 {author}",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft)、pywinrt 経由。UI: Tkinter、Pillow、pystray。"
                         "リンク先は Jisho.org です。",
        "close": "閉じる",
        "tray_show": "表示",
        "tray_listen": "クリップボードを監視",
        "tray_quit": "終了",
        "already_running": "Yomitoru Kanji Reader はすでに起動しています（通知領域を確認してください）。",
        "dict_missing": "KANJIDIC2 辞書がありません (data/kanjidic2.sqlite)。\n\n"
                        "今すぐダウンロードしますか？（約 1.5 MB、初回のみ）\n\n"
                        "次のコマンドでも作成できます:  python -m yomitoru.setup_dict",
        "dict_failed": "KANJIDIC2 辞書を準備できませんでした:\n{error}",
    },
    "zh": {
        "listening": "监听中",
        "off": "已关闭",
        "history": "历史",
        "options": "选项",
        "about_btn": "关于…",
        "search_btn": "搜索",
        "search_jisho": "在 jisho.org 搜索",
        "view_jisho": "在 jisho.org 查看",
        "copy": "复制",
        "copied": "已复制：{text}",
        "copy_kanji": "复制汉字",
        "no_text": "未识别到文字。请在上方输入后点击“搜索”。",
        "no_kanji": "文本中没有汉字。",
        "on": "音读",
        "kun": "训读",
        "meaning": "释义",
        "meaning_in_english": "（英语）",
        "not_in_dict": "KANJIDIC2 中未收录",
        "strokes": "{n} 画",
        "jlpt": "旧 JLPT {n} 级",
        "grade": "年级 {n}",
        "waiting": "等待截图 (Win+Shift+S)…",
        "paused": "已关闭：不会处理截图。",
        "recognizing": "识别中…",
        "captured_at": "截图时间：{when}",
        "searched_at": "搜索时间：{when}",
        "history_cleared": "历史记录已清除。",
        "ocr_error": "OCR 错误：{error}",
        "capture_no_ocr": "已收到截图，但 OCR 不可用。",
        "ocr_status_unavailable": "OCR 不可用：可以手动输入文字后点击“搜索”。",
        "ocr_title": "{app}：OCR 不可用",
        "ocr_install_help": (
            "未安装 Windows 日语 OCR。\n\n"
            "安装方法：\n"
            "  1. 打开 设置 → 时间和语言 → 语言和区域。\n"
            "  2. 在“首选语言”中点击“添加语言”。\n"
            "  3. 搜索“日语”（日本語）并选择。\n"
            "  4. 确认已勾选“光学字符识别(OCR)”（其他功能可选），然后安装。\n"
            "  5. 重新启动 Yomitoru Kanji Reader。\n\n"
            "无需更改 Windows 的显示语言。"
        ),
        "opt_bring_to_front": "截图时显示窗口",
        "opt_open_jisho": "截图时直接打开 jisho.org",
        "opened_jisho": "已在 jisho.org 打开：{text}",
        "opt_always_on_top": "窗口置顶",
        "opt_dark_mode": "深色模式",
        "opt_language": "语言",
        "today": "今天 {time}",
        "yesterday": "昨天 {time}",
        "date_fmt": "%m/%d %H:%M",
        "date_year_fmt": "%Y/%m/%d %H:%M",
        "hist_title": "历史记录",
        "hist_col_text": "文本",
        "hist_col_when": "时间",
        "hist_open": "打开",
        "hist_clear": "清除历史…",
        "hist_empty": "还没有搜索记录。\n用 Win+Shift+S 截取一个汉字吧。",
        "hist_confirm_title": "清除历史",
        "hist_confirm": "要删除所有历史记录吗？",
        "about_title": "关于 {app}",
        "about_version": "版本 {version}",
        "about_tagline": "用 Win+Shift+S 截取汉字，即可立即查看读音和释义。"
                         "无需联网：OCR 由 Windows 提供，词典已内置。",
        "about_author": "作者",
        "about_created_by": "作者：{author}",
        "about_source": "源代码",
        "about_releases": "新版本",
        "about_report": "报告问题",
        "about_dictionary": "词典",
        "about_dict_text": "本程序使用 Electronic Dictionary Research and Development Group (EDRDG) 所有的 "
                           "KANJIDIC2 文件（版本 {version}），并依照该组织的许可协议 Creative Commons "
                           "署名-相同方式共享 4.0 (CC BY-SA 4.0) 使用。",
        "about_kanjidic": "KANJIDIC 项目",
        "about_edrdg": "EDRDG 许可协议",
        "about_license": "许可与致谢",
        "about_code_license": "代码采用 MIT 许可 © 2026 {author}。",
        "about_credits": "OCR：Windows.Media.Ocr（Microsoft），通过 pywinrt。界面：Tkinter、Pillow 和 pystray。"
                         "链接指向 Jisho.org。",
        "close": "关闭",
        "tray_show": "显示",
        "tray_listen": "监听剪贴板",
        "tray_quit": "退出",
        "already_running": "Yomitoru Kanji Reader 已在运行（请查看系统托盘）。",
        "dict_missing": "缺少 KANJIDIC2 词典 (data/kanjidic2.sqlite)。\n\n"
                        "现在下载吗？（约 1.5 MB，仅需一次）\n\n"
                        "也可以运行以下命令生成：  python -m yomitoru.setup_dict",
        "dict_failed": "无法准备 KANJIDIC2 词典：\n{error}",
    },
    "ko": {
        "listening": "감시 중",
        "off": "꺼짐",
        "history": "기록",
        "options": "옵션",
        "about_btn": "정보…",
        "search_btn": "검색",
        "search_jisho": "jisho.org에서 검색",
        "view_jisho": "jisho.org에서 보기",
        "copy": "복사",
        "copied": "복사했습니다: {text}",
        "copy_kanji": "한자 복사",
        "no_text": "텍스트를 인식하지 못했습니다. 위에 입력하고 [검색]을 누르세요.",
        "no_kanji": "텍스트에 한자가 없습니다.",
        "on": "음독",
        "kun": "훈독",
        "meaning": "뜻",
        "meaning_in_english": "(영어)",
        "not_in_dict": "KANJIDIC2에 없습니다",
        "strokes": "{n}획",
        "jlpt": "구 JLPT {n}급",
        "grade": "학년 {n}",
        "waiting": "스크린샷을 기다리는 중 (Win+Shift+S)…",
        "paused": "꺼짐: 스크린샷을 처리하지 않습니다.",
        "recognizing": "인식 중…",
        "captured_at": "캡처: {when}",
        "searched_at": "검색: {when}",
        "history_cleared": "기록을 삭제했습니다.",
        "ocr_error": "OCR 오류: {error}",
        "capture_no_ocr": "스크린샷을 받았지만 OCR을 사용할 수 없습니다.",
        "ocr_status_unavailable": "OCR을 사용할 수 없습니다. 텍스트를 직접 입력하고 [검색]을 누르세요.",
        "ocr_title": "{app}: OCR 사용 불가",
        "ocr_install_help": (
            "Windows 일본어 OCR이 설치되어 있지 않습니다.\n\n"
            "설치 방법:\n"
            "  1. 설정 → 시간 및 언어 → 언어 및 지역을 엽니다.\n"
            "  2. '기본 설정 언어'에서 '언어 추가'를 클릭합니다.\n"
            "  3. '일본어'(日本語)를 검색하여 선택합니다.\n"
            "  4. '광학 문자 인식(OCR)'이 선택되어 있는지 확인하고 설치합니다 "
            "(다른 기능은 선택 사항입니다).\n"
            "  5. Yomitoru Kanji Reader를 다시 시작합니다.\n\n"
            "Windows 표시 언어를 바꿀 필요는 없습니다."
        ),
        "opt_bring_to_front": "캡처할 때 창 표시",
        "opt_open_jisho": "캡처할 때 jisho.org 바로 열기",
        "opened_jisho": "jisho.org에서 열었습니다: {text}",
        "opt_always_on_top": "항상 위에 표시",
        "opt_dark_mode": "다크 모드",
        "opt_language": "언어",
        "today": "오늘 {time}",
        "yesterday": "어제 {time}",
        "date_fmt": "%m/%d %H:%M",
        "date_year_fmt": "%Y/%m/%d %H:%M",
        "hist_title": "기록",
        "hist_col_text": "텍스트",
        "hist_col_when": "날짜",
        "hist_open": "열기",
        "hist_clear": "기록 삭제…",
        "hist_empty": "아직 검색 기록이 없습니다.\nWin+Shift+S로 한자를 캡처하세요.",
        "hist_confirm_title": "기록 삭제",
        "hist_confirm": "기록에서 모든 검색을 삭제할까요?",
        "about_title": "{app} 정보",
        "about_version": "버전 {version}",
        "about_tagline": "Win+Shift+S로 한자를 캡처하면 읽는 법과 뜻을 바로 볼 수 있습니다. "
                         "오프라인으로 동작합니다: OCR은 Windows 기본 기능이고 사전이 포함되어 있습니다.",
        "about_author": "만든 사람",
        "about_created_by": "만든 사람: {author}",
        "about_source": "소스 코드",
        "about_releases": "새 버전",
        "about_report": "버그 신고",
        "about_dictionary": "사전",
        "about_dict_text": "이 프로그램은 Electronic Dictionary Research and Development Group(EDRDG)이 "
                           "소유한 KANJIDIC2 파일(버전 {version})을 해당 그룹의 라이선스인 Creative Commons "
                           "저작자표시-동일조건변경허락 4.0(CC BY-SA 4.0)에 따라 사용합니다.",
        "about_kanjidic": "KANJIDIC 프로젝트",
        "about_edrdg": "EDRDG 라이선스",
        "about_license": "라이선스 및 크레딧",
        "about_code_license": "코드는 MIT 라이선스 © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr(Microsoft), pywinrt 사용. 인터페이스: Tkinter, Pillow, pystray. "
                         "링크는 Jisho.org로 연결됩니다.",
        "close": "닫기",
        "tray_show": "열기",
        "tray_listen": "클립보드 감시",
        "tray_quit": "종료",
        "already_running": "Yomitoru Kanji Reader가 이미 실행 중입니다 (알림 영역을 확인하세요).",
        "dict_missing": "KANJIDIC2 사전이 없습니다 (data/kanjidic2.sqlite).\n\n"
                        "지금 다운로드할까요? (약 1.5 MB, 한 번만)\n\n"
                        "다음 명령으로도 만들 수 있습니다:  python -m yomitoru.setup_dict",
        "dict_failed": "KANJIDIC2 사전을 준비하지 못했습니다:\n{error}",
    },
    "fr": {
        "listening": "À l'écoute",
        "off": "Désactivé",
        "history": "Historique",
        "options": "Options",
        "about_btn": "À propos…",
        "search_btn": "Chercher",
        "search_jisho": "Chercher sur jisho.org",
        "view_jisho": "Voir sur jisho.org",
        "copy": "Copier",
        "copied": "Copié : {text}",
        "copy_kanji": "Copier le kanji",
        "no_text": "Aucun texte reconnu. Saisissez-le ci-dessus et appuyez sur Chercher.",
        "no_kanji": "Aucun kanji dans le texte.",
        "on": "On",
        "kun": "Kun",
        "meaning": "Sens",
        "meaning_in_english": "(en anglais)",
        "not_in_dict": "Absent de KANJIDIC2",
        "strokes": "{n} traits",
        "jlpt": "JLPT {n} (ancien)",
        "grade": "niveau {n}",
        "waiting": "En attente d'une capture (Win+Shift+S)…",
        "paused": "Désactivé : les captures sont ignorées.",
        "recognizing": "Reconnaissance…",
        "captured_at": "Capturé : {when}",
        "searched_at": "Recherché : {when}",
        "history_cleared": "Historique effacé.",
        "ocr_error": "Erreur OCR : {error}",
        "capture_no_ocr": "Capture reçue, mais l'OCR n'est pas disponible.",
        "ocr_status_unavailable": "OCR indisponible : vous pouvez saisir le texte et appuyer sur Chercher.",
        "ocr_title": "{app} : OCR indisponible",
        "ocr_install_help": (
            "L'OCR japonais de Windows n'est pas installé.\n\n"
            "Pour l'installer :\n"
            "  1. Ouvrez Paramètres → Heure et langue → Langue et région.\n"
            "  2. Sous « Langues préférées », cliquez sur « Ajouter une langue ».\n"
            "  3. Recherchez « Japonais » (日本語) et sélectionnez-le.\n"
            "  4. Vérifiez que « Reconnaissance optique de caractères (OCR) » est cochée "
            "(les autres options sont facultatives) et installez.\n"
            "  5. Redémarrez Yomitoru Kanji Reader.\n\n"
            "Inutile de changer la langue d'affichage de Windows."
        ),
        "opt_bring_to_front": "Afficher la fenêtre à chaque capture",
        "opt_open_jisho": "Ouvrir directement jisho.org à chaque capture",
        "opened_jisho": "Ouvert sur jisho.org : {text}",
        "opt_always_on_top": "Toujours au premier plan",
        "opt_dark_mode": "Mode sombre",
        "opt_language": "Langue",
        "today": "aujourd'hui {time}",
        "yesterday": "hier {time}",
        "date_fmt": "%d/%m %H:%M",
        "date_year_fmt": "%d/%m/%Y %H:%M",
        "hist_title": "Historique",
        "hist_col_text": "Texte",
        "hist_col_when": "Date",
        "hist_open": "Ouvrir",
        "hist_clear": "Effacer l'historique…",
        "hist_empty": "Aucune recherche pour l'instant.\nCapturez un kanji avec Win+Shift+S.",
        "hist_confirm_title": "Effacer l'historique",
        "hist_confirm": "Effacer toutes les recherches de l'historique ?",
        "about_title": "À propos de {app}",
        "about_version": "Version {version}",
        "about_tagline": "Capturez un kanji avec Win+Shift+S et voyez aussitôt ses lectures et son sens. "
                         "Fonctionne hors ligne : l'OCR est celui de Windows et le dictionnaire est inclus.",
        "about_author": "Auteur",
        "about_created_by": "Créé par {author}.",
        "about_source": "Code source",
        "about_releases": "Nouvelles versions",
        "about_report": "Signaler un bug",
        "about_dictionary": "Dictionnaire",
        "about_dict_text": "Ce programme utilise le fichier KANJIDIC2 (version {version}), propriété de "
                           "l'Electronic Dictionary Research and Development Group (EDRDG), conformément à "
                           "la licence du groupe : Creative Commons Attribution - Partage dans les mêmes "
                           "conditions 4.0 (CC BY-SA 4.0).",
        "about_kanjidic": "Projet KANJIDIC",
        "about_edrdg": "Licence de l'EDRDG",
        "about_license": "Licence et crédits",
        "about_code_license": "Code sous licence MIT © 2026 {author}.",
        "about_credits": "OCR : Windows.Media.Ocr (Microsoft) via pywinrt. Interface : Tkinter, Pillow et pystray. "
                         "Les liens ouvrent Jisho.org.",
        "close": "Fermer",
        "tray_show": "Afficher",
        "tray_listen": "Écouter le presse-papiers",
        "tray_quit": "Quitter",
        "already_running": "Yomitoru Kanji Reader est déjà ouvert (cherchez-le dans la zone de notification).",
        "dict_missing": "Le dictionnaire KANJIDIC2 est absent (data/kanjidic2.sqlite).\n\n"
                        "Le télécharger maintenant ? (≈1,5 Mo, une seule fois)\n\n"
                        "Vous pouvez aussi le générer avec :  python -m yomitoru.setup_dict",
        "dict_failed": "Impossible de préparer le dictionnaire KANJIDIC2 :\n{error}",
    },
    "pt": {
        "listening": "Ouvindo",
        "off": "Desligado",
        "history": "Histórico",
        "options": "Opções",
        "about_btn": "Sobre…",
        "search_btn": "Buscar",
        "search_jisho": "Buscar no jisho.org",
        "view_jisho": "Ver no jisho.org",
        "copy": "Copiar",
        "copied": "Copiado: {text}",
        "copy_kanji": "Copiar o kanji",
        "no_text": "Nenhum texto reconhecido. Digite acima e clique em Buscar.",
        "no_kanji": "Não há kanji no texto.",
        "on": "On",
        "kun": "Kun",
        "meaning": "Significado",
        "meaning_in_english": "(em inglês)",
        "not_in_dict": "Não está no KANJIDIC2",
        "strokes": "{n} traços",
        "jlpt": "JLPT {n} (antigo)",
        "grade": "série {n}",
        "waiting": "Aguardando uma captura (Win+Shift+S)…",
        "paused": "Desligado: as capturas não são processadas.",
        "recognizing": "Reconhecendo…",
        "captured_at": "Capturado: {when}",
        "searched_at": "Buscado: {when}",
        "history_cleared": "Histórico apagado.",
        "ocr_error": "Erro de OCR: {error}",
        "capture_no_ocr": "Captura recebida, mas o OCR não está disponível.",
        "ocr_status_unavailable": "OCR indisponível: você pode digitar o texto e clicar em Buscar.",
        "ocr_title": "{app}: OCR indisponível",
        "ocr_install_help": (
            "O OCR japonês do Windows não está instalado.\n\n"
            "Para instalar:\n"
            "  1. Abra Configurações → Hora e idioma → Idioma e região.\n"
            "  2. Em “Idiomas preferenciais”, clique em “Adicionar um idioma”.\n"
            "  3. Procure “Japonês” (日本語) e selecione.\n"
            "  4. Verifique se “Reconhecimento óptico de caracteres (OCR)” está marcado "
            "(os outros recursos são opcionais) e instale.\n"
            "  5. Reinicie o Yomitoru Kanji Reader.\n\n"
            "Não é preciso mudar o idioma do Windows."
        ),
        "opt_bring_to_front": "Mostrar a janela ao capturar",
        "opt_open_jisho": "Abrir o jisho.org direto ao capturar",
        "opened_jisho": "Aberto no jisho.org: {text}",
        "opt_always_on_top": "Sempre visível",
        "opt_dark_mode": "Modo escuro",
        "opt_language": "Idioma",
        "today": "hoje {time}",
        "yesterday": "ontem {time}",
        "date_fmt": "%d/%m %H:%M",
        "date_year_fmt": "%d/%m/%Y %H:%M",
        "hist_title": "Histórico",
        "hist_col_text": "Texto",
        "hist_col_when": "Data",
        "hist_open": "Abrir",
        "hist_clear": "Apagar histórico…",
        "hist_empty": "Ainda não há buscas.\nCapture um kanji com Win+Shift+S.",
        "hist_confirm_title": "Apagar histórico",
        "hist_confirm": "Apagar todas as buscas do histórico?",
        "about_title": "Sobre o {app}",
        "about_version": "Versão {version}",
        "about_tagline": "Capture um kanji com Win+Shift+S e veja na hora suas leituras e seu significado. "
                         "Funciona offline: o OCR é o do Windows e o dicionário vem incluído.",
        "about_author": "Autor",
        "about_created_by": "Criado por {author}.",
        "about_source": "Código-fonte",
        "about_releases": "Novas versões",
        "about_report": "Relatar um erro",
        "about_dictionary": "Dicionário",
        "about_dict_text": "Este programa usa o arquivo KANJIDIC2 (versão {version}), propriedade do "
                           "Electronic Dictionary Research and Development Group (EDRDG), de acordo com a "
                           "licença do grupo: Creative Commons Atribuição-CompartilhaIgual 4.0 (CC BY-SA 4.0).",
        "about_kanjidic": "Projeto KANJIDIC",
        "about_edrdg": "Licença do EDRDG",
        "about_license": "Licença e créditos",
        "about_code_license": "Código sob licença MIT © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft) via pywinrt. Interface: Tkinter, Pillow e pystray. "
                         "Os links abrem o Jisho.org.",
        "close": "Fechar",
        "tray_show": "Mostrar",
        "tray_listen": "Ouvir a área de transferência",
        "tray_quit": "Sair",
        "already_running": "O Yomitoru Kanji Reader já está aberto (procure-o na bandeja do sistema).",
        "dict_missing": "Falta o dicionário KANJIDIC2 (data/kanjidic2.sqlite).\n\n"
                        "Baixar agora? (≈1,5 MB, só uma vez)\n\n"
                        "Você também pode gerá-lo com:  python -m yomitoru.setup_dict",
        "dict_failed": "Não foi possível preparar o dicionário KANJIDIC2:\n{error}",
    },
    "de": {
        "listening": "Hört zu",
        "off": "Aus",
        "history": "Verlauf",
        "options": "Optionen",
        "about_btn": "Über…",
        "search_btn": "Suchen",
        "search_jisho": "Auf jisho.org suchen",
        "view_jisho": "Auf jisho.org ansehen",
        "copy": "Kopieren",
        "copied": "Kopiert: {text}",
        "copy_kanji": "Kanji kopieren",
        "no_text": "Kein Text erkannt. Gib ihn oben ein und klicke auf Suchen.",
        "no_kanji": "Kein Kanji im Text.",
        "on": "On",
        "kun": "Kun",
        "meaning": "Bedeutung",
        "meaning_in_english": "(auf Englisch)",
        "not_in_dict": "Nicht in KANJIDIC2",
        "strokes": "{n} Striche",
        "jlpt": "JLPT {n} (alt)",
        "grade": "Stufe {n}",
        "waiting": "Warte auf einen Screenshot (Win+Shift+S)…",
        "paused": "Aus: Screenshots werden ignoriert.",
        "recognizing": "Erkenne…",
        "captured_at": "Aufgenommen: {when}",
        "searched_at": "Gesucht: {when}",
        "history_cleared": "Verlauf gelöscht.",
        "ocr_error": "OCR-Fehler: {error}",
        "capture_no_ocr": "Screenshot erhalten, aber die Texterkennung ist nicht verfügbar.",
        "ocr_status_unavailable": "Texterkennung nicht verfügbar: Gib den Text ein und klicke auf Suchen.",
        "ocr_title": "{app}: Texterkennung nicht verfügbar",
        "ocr_install_help": (
            "Die japanische Texterkennung (OCR) von Windows ist nicht installiert.\n\n"
            "So installierst du sie:\n"
            "  1. Öffne Einstellungen → Zeit und Sprache → Sprache und Region.\n"
            "  2. Klicke unter „Bevorzugte Sprachen“ auf „Sprache hinzufügen“.\n"
            "  3. Suche „Japanisch“ (日本語) und wähle es aus.\n"
            "  4. Achte darauf, dass „Optische Zeichenerkennung (OCR)“ aktiviert ist "
            "(der Rest ist optional), und installiere.\n"
            "  5. Starte Yomitoru Kanji Reader neu.\n\n"
            "Die Anzeigesprache von Windows musst du nicht ändern."
        ),
        "opt_bring_to_front": "Fenster bei jedem Screenshot anzeigen",
        "opt_open_jisho": "Bei Aufnahme direkt jisho.org öffnen",
        "opened_jisho": "Auf jisho.org geöffnet: {text}",
        "opt_always_on_top": "Immer im Vordergrund",
        "opt_dark_mode": "Dunkelmodus",
        "opt_language": "Sprache",
        "today": "heute {time}",
        "yesterday": "gestern {time}",
        "date_fmt": "%d.%m. %H:%M",
        "date_year_fmt": "%d.%m.%Y %H:%M",
        "hist_title": "Verlauf",
        "hist_col_text": "Text",
        "hist_col_when": "Datum",
        "hist_open": "Öffnen",
        "hist_clear": "Verlauf löschen…",
        "hist_empty": "Noch keine Suchen.\nNimm ein Kanji mit Win+Shift+S auf.",
        "hist_confirm_title": "Verlauf löschen",
        "hist_confirm": "Alle Suchen aus dem Verlauf löschen?",
        "about_title": "Über {app}",
        "about_version": "Version {version}",
        "about_tagline": "Nimm ein Kanji mit Win+Shift+S auf und sieh sofort seine Lesungen und Bedeutung. "
                         "Funktioniert offline: Die Texterkennung ist in Windows eingebaut, das Wörterbuch "
                         "ist enthalten.",
        "about_author": "Autor",
        "about_created_by": "Erstellt von {author}.",
        "about_source": "Quellcode",
        "about_releases": "Neue Versionen",
        "about_report": "Fehler melden",
        "about_dictionary": "Wörterbuch",
        "about_dict_text": "Dieses Programm verwendet die Datei KANJIDIC2 (Version {version}), Eigentum der "
                           "Electronic Dictionary Research and Development Group (EDRDG), gemäß der Lizenz der "
                           "Gruppe: Creative Commons Namensnennung – Weitergabe unter gleichen Bedingungen 4.0 "
                           "(CC BY-SA 4.0).",
        "about_kanjidic": "KANJIDIC-Projekt",
        "about_edrdg": "EDRDG-Lizenz",
        "about_license": "Lizenz und Danksagung",
        "about_code_license": "Code unter MIT-Lizenz © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft) über pywinrt. Oberfläche: Tkinter, Pillow und pystray. "
                         "Links öffnen Jisho.org.",
        "close": "Schließen",
        "tray_show": "Anzeigen",
        "tray_listen": "Zwischenablage überwachen",
        "tray_quit": "Beenden",
        "already_running": "Yomitoru Kanji Reader läuft bereits (sieh im Infobereich der Taskleiste nach).",
        "dict_missing": "Das Wörterbuch KANJIDIC2 fehlt (data/kanjidic2.sqlite).\n\n"
                        "Jetzt herunterladen? (≈1,5 MB, nur einmal)\n\n"
                        "Du kannst es auch erzeugen mit:  python -m yomitoru.setup_dict",
        "dict_failed": "Das Wörterbuch KANJIDIC2 konnte nicht vorbereitet werden:\n{error}",
    },
    "it": {
        "listening": "In ascolto",
        "off": "Spento",
        "history": "Cronologia",
        "options": "Opzioni",
        "about_btn": "Info…",
        "search_btn": "Cerca",
        "search_jisho": "Cerca su jisho.org",
        "view_jisho": "Vedi su jisho.org",
        "copy": "Copia",
        "copied": "Copiato: {text}",
        "copy_kanji": "Copia il kanji",
        "no_text": "Nessun testo riconosciuto. Scrivilo sopra e premi Cerca.",
        "no_kanji": "Nessun kanji nel testo.",
        "on": "On",
        "kun": "Kun",
        "meaning": "Significato",
        "meaning_in_english": "(in inglese)",
        "not_in_dict": "Non presente in KANJIDIC2",
        "strokes": "{n} tratti",
        "jlpt": "JLPT {n} (vecchio)",
        "grade": "grado {n}",
        "waiting": "In attesa di uno screenshot (Win+Shift+S)…",
        "paused": "Spento: gli screenshot vengono ignorati.",
        "recognizing": "Riconoscimento…",
        "captured_at": "Catturato: {when}",
        "searched_at": "Cercato: {when}",
        "history_cleared": "Cronologia cancellata.",
        "ocr_error": "Errore OCR: {error}",
        "capture_no_ocr": "Screenshot ricevuto, ma l'OCR non è disponibile.",
        "ocr_status_unavailable": "OCR non disponibile: puoi scrivere il testo e premere Cerca.",
        "ocr_title": "{app}: OCR non disponibile",
        "ocr_install_help": (
            "L'OCR giapponese di Windows non è installato.\n\n"
            "Per installarlo:\n"
            "  1. Apri Impostazioni → Data/ora e lingua → Lingua e area geografica.\n"
            "  2. In «Lingue preferite», fai clic su «Aggiungi una lingua».\n"
            "  3. Cerca «Giapponese» (日本語) e selezionalo.\n"
            "  4. Assicurati che «Riconoscimento ottico dei caratteri (OCR)» sia selezionato "
            "(le altre funzionalità sono facoltative) e installa.\n"
            "  5. Riavvia Yomitoru Kanji Reader.\n\n"
            "Non serve cambiare la lingua di Windows."
        ),
        "opt_bring_to_front": "Mostra la finestra a ogni cattura",
        "opt_open_jisho": "Apri direttamente jisho.org a ogni cattura",
        "opened_jisho": "Aperto su jisho.org: {text}",
        "opt_always_on_top": "Sempre in primo piano",
        "opt_dark_mode": "Modalità scura",
        "opt_language": "Lingua",
        "today": "oggi {time}",
        "yesterday": "ieri {time}",
        "date_fmt": "%d/%m %H:%M",
        "date_year_fmt": "%d/%m/%Y %H:%M",
        "hist_title": "Cronologia",
        "hist_col_text": "Testo",
        "hist_col_when": "Data",
        "hist_open": "Apri",
        "hist_clear": "Cancella cronologia…",
        "hist_empty": "Ancora nessuna ricerca.\nCattura un kanji con Win+Shift+S.",
        "hist_confirm_title": "Cancella cronologia",
        "hist_confirm": "Cancellare tutte le ricerche dalla cronologia?",
        "about_title": "Informazioni su {app}",
        "about_version": "Versione {version}",
        "about_tagline": "Cattura un kanji con Win+Shift+S e vedi subito le sue letture e il suo significato. "
                         "Funziona offline: l'OCR è quello di Windows e il dizionario è incluso.",
        "about_author": "Autore",
        "about_created_by": "Creato da {author}.",
        "about_source": "Codice sorgente",
        "about_releases": "Nuove versioni",
        "about_report": "Segnala un errore",
        "about_dictionary": "Dizionario",
        "about_dict_text": "Questo programma usa il file KANJIDIC2 (versione {version}), di proprietà "
                           "dell'Electronic Dictionary Research and Development Group (EDRDG), in conformità "
                           "con la licenza del gruppo: Creative Commons Attribuzione - Condividi allo stesso "
                           "modo 4.0 (CC BY-SA 4.0).",
        "about_kanjidic": "Progetto KANJIDIC",
        "about_edrdg": "Licenza EDRDG",
        "about_license": "Licenza e riconoscimenti",
        "about_code_license": "Codice con licenza MIT © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft) tramite pywinrt. Interfaccia: Tkinter, Pillow e "
                         "pystray. I link aprono Jisho.org.",
        "close": "Chiudi",
        "tray_show": "Mostra",
        "tray_listen": "Ascolta gli appunti",
        "tray_quit": "Esci",
        "already_running": "Yomitoru Kanji Reader è già aperto (cercalo nell'area di notifica).",
        "dict_missing": "Manca il dizionario KANJIDIC2 (data/kanjidic2.sqlite).\n\n"
                        "Scaricarlo ora? (≈1,5 MB, una sola volta)\n\n"
                        "Puoi anche generarlo con:  python -m yomitoru.setup_dict",
        "dict_failed": "Impossibile preparare il dizionario KANJIDIC2:\n{error}",
    },
    "ru": {
        "listening": "Слушает",
        "off": "Выключено",
        "history": "История",
        "options": "Настройки",
        "about_btn": "О программе",
        "search_btn": "Найти",
        "search_jisho": "Искать на jisho.org",
        "view_jisho": "Открыть на jisho.org",
        "copy": "Копировать",
        "copied": "Скопировано: {text}",
        "copy_kanji": "Копировать кандзи",
        "no_text": "Текст не распознан. Введите его выше и нажмите «Найти».",
        "no_kanji": "В тексте нет кандзи.",
        "on": "Он",
        "kun": "Кун",
        "meaning": "Значение",
        "meaning_in_english": "(на английском)",
        "not_in_dict": "Нет в KANJIDIC2",
        "strokes": "черт: {n}",
        "jlpt": "JLPT {n} (старый)",
        "grade": "класс {n}",
        "waiting": "Ожидание снимка экрана (Win+Shift+S)…",
        "paused": "Выключено: снимки экрана не обрабатываются.",
        "recognizing": "Распознавание…",
        "captured_at": "Снимок: {when}",
        "searched_at": "Поиск: {when}",
        "history_cleared": "История очищена.",
        "ocr_error": "Ошибка OCR: {error}",
        "capture_no_ocr": "Снимок получен, но OCR недоступно.",
        "ocr_status_unavailable": "OCR недоступно: введите текст вручную и нажмите «Найти».",
        "ocr_title": "{app}: OCR недоступно",
        "ocr_install_help": (
            "Японское распознавание текста (OCR) Windows не установлено.\n\n"
            "Как установить:\n"
            "  1. Откройте Параметры → Время и язык → Язык и регион.\n"
            "  2. В разделе «Предпочитаемые языки» нажмите «Добавить язык».\n"
            "  3. Найдите «Японский» (日本語) и выберите его.\n"
            "  4. Убедитесь, что отмечено «Оптическое распознавание символов (OCR)» "
            "(остальное — по желанию), и установите.\n"
            "  5. Перезапустите Yomitoru Kanji Reader.\n\n"
            "Менять язык интерфейса Windows не нужно."
        ),
        "opt_bring_to_front": "Показывать окно при снимке",
        "opt_open_jisho": "Сразу открывать jisho.org при снимке",
        "opened_jisho": "Открыто на jisho.org: {text}",
        "opt_always_on_top": "Поверх всех окон",
        "opt_dark_mode": "Тёмная тема",
        "opt_language": "Язык",
        "today": "сегодня {time}",
        "yesterday": "вчера {time}",
        "date_fmt": "%d.%m %H:%M",
        "date_year_fmt": "%d.%m.%Y %H:%M",
        "hist_title": "История",
        "hist_col_text": "Текст",
        "hist_col_when": "Дата",
        "hist_open": "Открыть",
        "hist_clear": "Очистить историю…",
        "hist_empty": "Пока нет запросов.\nСделайте снимок кандзи с помощью Win+Shift+S.",
        "hist_confirm_title": "Очистить историю",
        "hist_confirm": "Удалить все запросы из истории?",
        "about_title": "О программе {app}",
        "about_version": "Версия {version}",
        "about_tagline": "Сделайте снимок кандзи с помощью Win+Shift+S и сразу увидите его чтения и значение. "
                         "Работает без интернета: OCR встроено в Windows, словарь входит в программу.",
        "about_author": "Автор",
        "about_created_by": "Автор: {author}.",
        "about_source": "Исходный код",
        "about_releases": "Новые версии",
        "about_report": "Сообщить об ошибке",
        "about_dictionary": "Словарь",
        "about_dict_text": "Эта программа использует файл KANJIDIC2 (версия {version}), принадлежащий "
                           "Electronic Dictionary Research and Development Group (EDRDG), в соответствии с "
                           "лицензией группы: Creative Commons «Атрибуция — На тех же условиях» 4.0 "
                           "(CC BY-SA 4.0).",
        "about_kanjidic": "Проект KANJIDIC",
        "about_edrdg": "Лицензия EDRDG",
        "about_license": "Лицензия и благодарности",
        "about_code_license": "Код распространяется по лицензии MIT © 2026 {author}.",
        "about_credits": "OCR: Windows.Media.Ocr (Microsoft) через pywinrt. Интерфейс: Tkinter, Pillow и pystray. "
                         "Ссылки ведут на Jisho.org.",
        "close": "Закрыть",
        "tray_show": "Показать",
        "tray_listen": "Следить за буфером обмена",
        "tray_quit": "Выход",
        "already_running": "Yomitoru Kanji Reader уже запущен (найдите его в области уведомлений).",
        "dict_missing": "Нет словаря KANJIDIC2 (data/kanjidic2.sqlite).\n\n"
                        "Скачать сейчас? (≈1,5 МБ, только один раз)\n\n"
                        "Его также можно создать командой:  python -m yomitoru.setup_dict",
        "dict_failed": "Не удалось подготовить словарь KANJIDIC2:\n{error}",
    },
}


class Translator:
    def __init__(self, lang: str = DEFAULT_LANGUAGE):
        self.lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE

    def __call__(self, key: str, **kwargs) -> str:
        text = STRINGS[self.lang].get(key)
        if text is None:
            text = STRINGS[DEFAULT_LANGUAGE].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def format_when(self, when: datetime, now: datetime | None = None) -> str:
        """'today 18:35', 'yesterday 09:10' or the date in the language's format."""
        now = now or datetime.now()
        days = (now.date() - when.date()).days
        time = f"{when:%H:%M}"
        if days == 0:
            return self("today", time=time)
        if days == 1:
            return self("yesterday", time=time)
        return when.strftime(self("date_fmt" if when.year == now.year else "date_year_fmt"))
