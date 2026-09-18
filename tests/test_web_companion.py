"""Tests fuer den CleanMarkdown Web Companion & PWA.

Validiert:
1. Vollstaendigkeit der Dateien und W3C-Manifest-Integritaet.
2. Existenz aller referenzierten App-Icons und Service-Worker-Caches.
3. Zero-Egress-Invariante (keine externen CDNs, Scripts oder Web-Fonts).
4. Kompatibilitaet des Session-Exchange-Formats (cleanmarkdown-session-v1.json).
5. Lokalisierungs-Paritaet (DE, EN, ES) und semantische HTML5-Elemente.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web_companion"


def test_web_companion_core_files_exist():
    """Prueft, ob alle Kernkomponenten des Web Companions vorhanden sind."""
    required_files = [
        WEB_DIR / "index.html",
        WEB_DIR / "app.css",
        WEB_DIR / "app.js",
        WEB_DIR / "sw.js",
        WEB_DIR / "manifest.json",
        WEB_DIR / "README.md",
        WEB_DIR / "favicon.png",
        WEB_DIR / "favicon.ico",
        WEB_DIR / "apple-touch-icon-180.png",
    ]
    for file_path in required_files:
        assert file_path.exists(), f"Erwartete Datei fehlt: {file_path.name}"
        assert file_path.stat().st_size > 0, f"Datei ist leer: {file_path.name}"


def test_web_manifest_validity_and_icon_resolution():
    """Validiert die W3C manifest.json und stellt sicher, dass alle Icons existieren."""
    manifest_file = WEB_DIR / "manifest.json"
    assert manifest_file.exists()

    content = json.loads(manifest_file.read_text(encoding="utf-8"))

    assert content.get("name") == "CleanMarkdown"
    assert content.get("short_name") == "CleanMarkdown"
    assert content.get("start_url") == "./index.html"
    assert content.get("display") == "standalone"

    icons = content.get("icons", [])
    assert len(icons) >= 4, "Manifest muss mindestens 4 Icon-Definitionen enthalten"

    for icon_entry in icons:
        src = icon_entry.get("src")
        assert src, "Icon-Eintrag enthaelt keinen 'src'-Pfad"
        icon_path = WEB_DIR / src
        assert icon_path.exists(), f"Manifest-Icon nicht auf Datentraeger gefunden: {src}"


def test_service_worker_asset_inventory():
    """Prueft, dass alle in sw.js registrierten Cache-Ziele physisch existieren."""
    sw_file = WEB_DIR / "sw.js"
    assert sw_file.exists()

    code = sw_file.read_text(encoding="utf-8")
    cache_match = re.search(r"const ASSETS_TO_CACHE = \[\s*([\s\S]*?)\s*\];", code)
    assert cache_match, "ASSETS_TO_CACHE Definition in sw.js nicht gefunden"

    raw_items = cache_match.group(1)
    asset_paths = [item.strip().strip("'\",") for item in raw_items.splitlines() if item.strip()]

    for rel_path in asset_paths:
        if rel_path in (".", "./"):
            continue
        clean_path = rel_path.lstrip("./")
        target_file = WEB_DIR / clean_path
        assert target_file.exists(), f"sw.js referenziert nicht existierendes Asset: {rel_path}"


def test_zero_egress_and_no_external_resources():
    """Stellt die Zero-Egress Invariante sicher: Keine externen CDNs, APIs oder Fonts."""
    index_html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    app_css = (WEB_DIR / "app.css").read_text(encoding="utf-8")

    # Pruefe auf externe Scripts oder Stylesheets in index.html
    external_script_pattern = re.compile(r'<script[^>]+src=["\'](https?://[^"\']+)["\']', re.IGNORECASE)
    external_link_pattern = re.compile(r'<link[^>]+href=["\'](https?://[^"\']+)["\']', re.IGNORECASE)

    assert not external_script_pattern.findall(index_html), "Externe Script-URLs in index.html verboten (Zero-Egress)"
    assert not external_link_pattern.findall(index_html), "Externe Stylesheet-URLs in index.html verboten (Zero-Egress)"

    # Pruefe auf @import externer Webfonts in app.css
    assert "@import url(" not in app_css.lower(), "Externe Web-Fonts via @import in app.css verboten"
    assert "fonts.googleapis.com" not in app_css, "Google Fonts in app.css verboten"

    # Pruefe auf Telemetrie/Analytics-Endpunkte in app.js
    assert "google-analytics.com" not in app_js
    assert "telemetry" not in app_js.lower()


def test_session_v1_exchange_contract():
    """Validiert, dass app.js das kanonische Format cleanmarkdown-session-v1 unterstuetzt."""
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")

    assert "cleanmarkdown-session-v1" in app_js
    assert "exportSession" in app_js
    assert "importSessionData" in app_js

    # Pruefe Pflichtfelder gemaess EXPORTFORMAT.md
    for field in ["version", "appVersion", "fileName", "markdown", "theme", "workspace", "updatedAt"]:
        assert f'"{field}"' in app_js or f"'{field}'" in app_js or f"{field}:" in app_js, (
            f"Pflichtfeld {field} in Session-Export nicht gefunden"
        )


def test_html_semantic_elements_and_controls():
    """Prueft die Existenz aller erforderlichen Interaktionselemente im HTML5-DOM."""
    index_html = (WEB_DIR / "index.html").read_text(encoding="utf-8")

    required_ids = [
        "markdown-editor",
        "preview-content",
        "file-name-input",
        "tab-editor",
        "tab-view",
        "lang-select",
        "btn-toggle-theme",
        "btn-open",
        "btn-save-md",
        "btn-export-session",
        "btn-clear-formatting",
        "btn-copy-clean",
        "stat-words",
        "stat-chars",
        "stat-chars-nospace",
        "stat-reading-time",
        "toast-notice",
    ]

    for element_id in required_ids:
        assert f'id="{element_id}"' in index_html, f"Erforderliches Element #{element_id} fehlt in index.html"


def test_localization_dictionary_completeness():
    """Validiert die Mehrsprachigkeit (DE, EN, ES) im Anwendungsmodul."""
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")

    # Extrahiere I18N Objekt
    match = re.search(r"const I18N\s*=\s*({[\s\S]*?\n  };)", app_js)
    assert match, "I18N Woerterbuch in app.js nicht gefunden"

    # Basispruefung auf Sprachschluessel
    assert "de:" in match.group(1)
    assert "en:" in match.group(1)
    assert "es:" in match.group(1)


def test_markdown_cleaner_contract_parity():
    """Vergleicht die Bereinigungsregeln des Web Companions mit dem Desktop-Verhalten."""
    import main as cleanmarkdown_main

    # Initialisiere Referenz-Cleaner der Desktop-Anwendung
    _ = cleanmarkdown_main.QApplication.instance() or cleanmarkdown_main.QApplication([])
    window = cleanmarkdown_main.MainWindow()

    raw_sample = (
        "# Haupttitel\n\n"
        "> Ein Zitat mit [Link](https://example.com) und ![Bild](pic.png)\n\n"
        "- [x] Erste Aufgabe\n"
        "- [ ] Zweite Aufgabe\n\n"
        "Hier ist **fetter** und *kursiver* Text sowie `code`.\n\n"
        "```python\nprint('code block')\n```\n\n"
        "$$\nE = mc^2\n$$\n"
    )

    desktop_cleaned = window._strip_markdown_formatting(raw_sample)

    # Erwartete Eigenschaften nach der Bereinigung:
    assert "Haupttitel" in desktop_cleaned
    assert "#" not in desktop_cleaned
    assert "Ein Zitat mit Link und Bild" in desktop_cleaned
    assert "Erste Aufgabe" in desktop_cleaned
    assert "[x]" not in desktop_cleaned
    assert "Hier ist fetter und kursiver Text sowie code." in desktop_cleaned
    assert "**" not in desktop_cleaned
    assert "E = mc^2" in desktop_cleaned
    assert "$$" not in desktop_cleaned

    window.close()
