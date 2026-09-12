"""Store-Screenshot-Generator für CleanMarkdown.

Erzeugt die Windows-Store-Screenshots aus der echten MainWindow, mit
gerendertem, lesbarem Text (KEIN Tofu).

WICHTIG (Root-Cause des Tofu-Bugs): Unter QT_QPA_PLATFORM=offscreen rendert
Qt auf Windows KEINE echten Glyphen -- jede Glyphe wird als .notdef-Kästchen
(Tofu) gerastert. window.grab() liefert dann ein Bild voller Kästchen.
Fix: native Plattform verwenden und das Fenster mit Qt.WA_DontShowOnScreen
unsichtbar halten. Dann lädt Qt die echte Font-Engine und grab() liefert
echten Text -- ohne dass ein Fenster sichtbar auf dem Bildschirm erscheint.

Zusätzlich prüft _assert_font_rendering() VOR dem Capture, dass echte
Glyphen gerendert werden, und bricht mit klarem Fehler ab, statt still Tofu
zu speichern.

Aufruf:
    PYTHONIOENCODING=utf-8 python generate_store_screenshots.py [--out DIR]
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QFont
from PySide6.QtWidgets import QApplication

from main import MainWindow  # noqa: E402


def _force_native_platform() -> None:
    """Entfernt eine erzwungene offscreen-Plattform VOR der QApplication-Erzeugung.

    Bewusst NICHT auf Modulebene, damit der blosse Import (z. B. in der
    pytest-Suite, die conftest-seitig offscreen setzt) die Umgebung nicht
    veraendert. Nur der echte Generierungslauf erzwingt die native Plattform.
    """
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        del os.environ["QT_QPA_PLATFORM"]


def _isolate_appdata() -> None:
    """Leitet %APPDATA% auf ein frisches Temp-Verzeichnis um.

    Damit laedt SettingsStore deterministische Default-Settings, statt die reale
    Nutzer-``settings.json`` -- die von parallelen Test-/App-Laeufen mit kaputten
    Werten (z. B. ungueltiger output_dir) kontaminiert sein kann und dann einen
    blockierenden Modal-Dialog ausloest. Der Generator soll reproduzierbar und
    unabhaengig von der Live-Konfiguration rendern.
    """
    import tempfile

    isolated = Path(tempfile.mkdtemp(prefix="cleanmarkdown-store-")) / "appdata"
    isolated.mkdir(parents=True, exist_ok=True)
    os.environ["APPDATA"] = str(isolated)


SAMPLE_MARKDOWN = """\
# Projektnotizen: Quartalsbericht

Willkommen bei **CleanMarkdown** -- dem schlanken Editor zum Lesen,
Bearbeiten und Exportieren von Markdown, ganz *ohne Cloud-Zwang*.

## Aufgaben dieser Woche

- [x] Rohdaten aus dem Export zusammenführen
- [x] Kennzahlen gegen das Vorquartal prüfen
- [ ] Präsentation für das Team vorbereiten
- [ ] Feedback von Anna und Björn einholen

## Kennzahlen im Überblick

| Bereich      | Q2      | Q3      | Trend |
|--------------|---------|---------|-------|
| Umsatz       | 128.400 | 141.900 | steigend |
| Neukunden    | 312     | 358     | steigend |
| Retouren     | 4,2 %   | 3,7 %   | fallend  |

> Merke: Zahlen sind vorläufig und werden nach dem Monatsabschluss final geprüft.

## Codebeispiel

```python
def wachstum(alt: float, neu: float) -> float:
    return (neu - alt) / alt * 100

print(f"Wachstum: {wachstum(128400, 141900):.1f} %")
```

Mehr dazu unter [der internen Dokumentation](https://example.org/docs).
Umlaute funktionieren einwandfrei: ä ö ü Ä Ö Ü ß.
"""

SAMPLE_READING_MARKDOWN = SAMPLE_MARKDOWN

SAMPLE_EDITOR_MARKDOWN = """\
# Notizen zum Projekt-Setup

## 1. Architektur und Datenhaltung

CleanMarkdown setzt auf klare Trennung:
- Lokale Textdateien (.md, .markdown) als primäre Datenquelle
- Einstellungen in `%APPDATA%\\CleanMarkdown\\settings.json`
- Optionales Session-Austauschformat `cleanmarkdown-session-v1.json`

## 2. Nächste Schritte

1. Formatleiste für Tabellen und Listen verwenden
2. Automatische Speicherung prüfen (Intervall: 30 Sekunden)
3. PDF-Export für den Entwurf erzeugen

```markdown
# Beispiel-Überschrift
- Aufzählungspunkt 1
- Aufzählungspunkt 2
```

*(Zuletzt geändert: vor 2 Minuten — Automatisch gesichert)*
"""

SAMPLE_MOBILE_SESSION_MARKDOWN = """\
# Mobile Companion & Session Sync

CleanMarkdown unterstützt das standardisierte Austauschformat
`cleanmarkdown-session-v1.json` für den nahtlosen Wechsel zwischen
Desktop-Arbeitsplatz und Smartphone (Flutter Mobile Line).

## Session-Metadaten

- **Format-Version:** `cleanmarkdown-session-v1.json`
- **Wortanzahl:** 428 Wörter
- **Zeichen:** 2.915 Zeichen
- **Geschätzte Lesezeit:** ~2,1 Minuten
- **Schutz:** Keine Cloud-Übertragung, rein dateibasierter Transfer

```json
{
  "version": "cleanmarkdown-session-v1",
  "document_title": "Projektbericht 2026",
  "stats": {
    "words": 428,
    "characters": 2915,
    "reading_time_minutes": 2.1
  },
  "created_at": "2026-09-12T14:30:00Z"
}
```

Die mobile Version bietet dieselbe ablenkungsfreie Leseerfahrung
sowie Textbereinigung für unterwegs.
"""


def _render_char(ch: str, font: QFont, size: QSize) -> bytes:
    pm = QPixmap(size)
    pm.fill(Qt.white)
    p = QPainter(pm)
    p.setFont(font)
    p.drawText(pm.rect(), Qt.AlignCenter, ch)
    p.end()
    return bytes(pm.toImage().constBits())


def font_rendering_works(app: QApplication) -> bool:
    """True, wenn die aktuelle Plattform echte Glyphen rendert.

    Rendert mehrere unterschiedliche Zeichen einzeln. Bei echtem Rendering
    sehen sie verschieden aus; bei Tofu ist jedes das gleiche .notdef-Kaestchen
    -> alle Renderings identisch.
    """
    font = app.font()
    size = QSize(48, 48)
    probes = ["A", "B", "g", "8", "M"]
    renders = [_render_char(ch, font, size) for ch in probes]
    blank = _render_char(" ", font, size)
    distinct = len(set(renders))
    non_blank = sum(1 for r in renders if r != blank)
    return distinct >= 3 and non_blank >= len(probes) - 1


def _assert_font_rendering(app: QApplication) -> None:
    platform = QApplication.platformName()
    if platform == "offscreen":
        raise RuntimeError(
            "Qt laeuft unter der 'offscreen'-Plattform -- Screenshots wuerden Tofu "
            "(Kaestchen statt Text) enthalten. QT_QPA_PLATFORM=offscreen nicht setzen; "
            "der Generator nutzt WA_DontShowOnScreen auf der nativen Plattform."
        )
    if not font_rendering_works(app):
        raise RuntimeError(
            f"Font-Rendering-Selbsttest fehlgeschlagen (Plattform '{platform}'): "
            "gerenderte Glyphen sind nicht unterscheidbar (Tofu-Verdacht). "
            "Abbruch, um kein defektes Screenshot-Set zu erzeugen."
        )


def _make_window(
    theme: str,
    tab_index: int,
    content: str = SAMPLE_MARKDOWN,
    width: int = 1400,
    height: int = 900,
) -> MainWindow:
    win = MainWindow()
    # Fenster nie sichtbar zeigen, aber echtes Rendering auf nativer Plattform.
    win.setAttribute(Qt.WA_DontShowOnScreen, True)
    win.settings.theme = theme
    win.resize(width, height)
    win.editor.setPlainText(content)
    win.is_modified = False
    win._render_preview()
    win._apply_theme()
    win.tabs.setCurrentIndex(tab_index)
    win.show()
    return win


def _capture(win: MainWindow, output_path: Path) -> None:
    app = QApplication.instance()
    app.processEvents()
    app.processEvents()
    pixmap = win.grab()
    if pixmap.isNull():
        raise RuntimeError(f"Screenshot ist null: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not pixmap.save(str(output_path), "PNG"):
        raise RuntimeError(f"Screenshot konnte nicht gespeichert werden: {output_path}")


# (Dateiname, Theme, Tab-Index)  Tab 0 = Reading/Viewer, 1 = Editor
SHOTS = [
    ("editor-dark.png", "dark", 1),
    ("reading-bright.png", "bright", 0),
    ("reading-dark.png", "dark", 0),
]

# 4 Standard 16:9 Presentation Screenshots (1920x1080) for Partner Center
STANDARD_STORE_SHOTS = [
    ("01_lesemodus-vorschau.png", "bright", 0, SAMPLE_READING_MARKDOWN, 1920, 1080),
    ("02_raw-editor-struktur.png", "bright", 1, SAMPLE_EDITOR_MARKDOWN, 1920, 1080),
    ("03_dark-mode-theme.png", "dark", 0, SAMPLE_READING_MARKDOWN, 1920, 1080),
    ("04_mobile-companion-session.png", "dark", 1, SAMPLE_MOBILE_SESSION_MARKDOWN, 1920, 1080),
]


def render_store_screenshots(
    output_dir: Path | None = None,
    package_dir: Path | None = None,
) -> list[Path]:
    _force_native_platform()
    _isolate_appdata()
    app = QApplication.instance() or QApplication(sys.argv)
    _assert_font_rendering(app)

    if output_dir is None:
        output_dir = PROJECT_ROOT / "README" / "screenshots" / "store"
    if package_dir is None:
        package_dir = PROJECT_ROOT / "store_package" / "CleanMarkdown" / "screenshots"

    output_dir.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    # 1. Render legacy shots into output_dir
    for filename, theme, tab_index in SHOTS:
        win = _make_window(theme, tab_index)
        target = output_dir / filename
        _capture(win, target)
        win.is_modified = False
        win.close()
        app.processEvents()
        written.append(target)

    # 2. Render 16:9 standard shots into output_dir and package_dir
    for filename, theme, tab_index, content, w, h in STANDARD_STORE_SHOTS:
        win = _make_window(theme, tab_index, content=content, width=w, height=h)
        target1 = output_dir / filename
        _capture(win, target1)
        written.append(target1)

        target2 = package_dir / filename
        shutil.copyfile(target1, target2)
        written.append(target2)

        win.is_modified = False
        win.close()
        app.processEvents()

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Store-Screenshots für CleanMarkdown")
    parser.add_argument(
        "--out",
        default=str(PROJECT_ROOT / "README" / "screenshots" / "store"),
        help="Zielordner (Standard: README/screenshots/store)",
    )
    args = parser.parse_args()
    out = Path(args.out)
    written = render_store_screenshots(out)
    print(f"{len(written)} Store-Screenshots erzeugt in {out}:")
    for path in written:
        print(f"  - {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
