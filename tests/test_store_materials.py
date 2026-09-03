"""Store-Material-Tests für CleanMarkdown.

Prüft, ob alle für den Windows Store benötigten Artefakte vorhanden und
inhaltlich korrekt sind.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

try:
    from PySide6.QtWidgets import QApplication
    _HAS_QT = True
except Exception:  # pragma: no cover - Qt sollte in der Test-Umgebung vorhanden sein
    _HAS_QT = False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = PROJECT_ROOT / "generate_store_screenshots.py"
STORE_SHOTS = ("editor-dark.png", "reading-bright.png", "reading-dark.png")


def test_store_package_json_exists_and_valid():
    path = PROJECT_ROOT / "store_package.json"
    assert path.exists(), "store_package.json fehlt"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["app_name"] == "CleanMarkdown"
    assert "logo" in data and data["logo"] != "PENDING"
    assert "languages" in data and len(data["languages"]) >= 2


def test_store_listing_has_de_and_en():
    path = PROJECT_ROOT / "STORE_LISTING.md"
    assert path.exists(), "STORE_LISTING.md fehlt"
    content = path.read_text(encoding="utf-8")
    assert "Deutsch" in content or "## DE" in content or "German" in content
    assert "English" in content or "## EN" in content


def test_privacy_policy_mentions_local():
    path = PROJECT_ROOT / "PRIVACY_POLICY.md"
    assert path.exists(), "PRIVACY_POLICY.md fehlt"
    content = path.read_text(encoding="utf-8").lower()
    assert "lokal" in content or "local" in content


def test_support_md_exists():
    path = PROJECT_ROOT / "SUPPORT.md"
    assert path.exists(), "SUPPORT.md fehlt"
    content = path.read_text(encoding="utf-8")
    assert "%APPDATA%\\CleanMarkdown\\settings.json" in content
    assert "QSettings" not in content


def test_privacy_policy_names_actual_settings_store():
    content = (PROJECT_ROOT / "PRIVACY_POLICY.md").read_text(encoding="utf-8")
    assert "%APPDATA%\\CleanMarkdown\\settings.json" in content
    assert "QSettings" not in content


def test_windows_store_prep_exists():
    path = PROJECT_ROOT / "WINDOWS_STORE_PREP.md"
    assert path.exists(), "WINDOWS_STORE_PREP.md fehlt"


def test_screenshot_store_dir_exists():
    path = PROJECT_ROOT / "README" / "screenshots" / "store"
    assert path.is_dir(), "README/screenshots/store/ fehlt"


# --- Store-Screenshot-Tofu-Regression (Welle-1-U3) --------------------------
# Hintergrund: Unter QT_QPA_PLATFORM=offscreen rendert Qt auf Windows keine
# echten Glyphen; window.grab() liefert dann Tofu (.notdef-Kaestchen statt
# Text). conftest.py erzwingt offscreen fuer die gesamte Suite -- daher pruefen
# diese Tests, dass der Generator diesen Zustand ERKENNT und mit klarem Fehler
# abbricht, statt still ein defektes Screenshot-Set zu erzeugen.


GENERATOR_PATH = PROJECT_ROOT / "generate_store_screenshots.py"

STORE_SHOTS = ("editor-dark.png", "reading-bright.png", "reading-dark.png")


def test_store_screenshot_generator_exists():
    assert GENERATOR_PATH.exists(), "generate_store_screenshots.py fehlt"


def test_store_screenshots_present_and_nonempty():
    store_dir = PROJECT_ROOT / "README" / "screenshots" / "store"
    for name in STORE_SHOTS:
        path = store_dir / name
        assert path.is_file(), f"Store-Screenshot {name} fehlt"
        assert path.stat().st_size > 0, f"Store-Screenshot {name} ist leer"


def test_generator_source_uses_native_platform_not_offscreen():
    """Statische Absicherung gegen Rueckfall in den Tofu-Modus."""
    src = GENERATOR_PATH.read_text(encoding="utf-8")
    assert "WA_DontShowOnScreen" in src, "Fix (WA_DontShowOnScreen) fehlt im Generator"
    forces_offscreen = re.search(
        r"""environ\[["']QT_QPA_PLATFORM["']\]\s*=\s*["']offscreen["']""", src
    )
    assert not forces_offscreen, "Generator darf QT_QPA_PLATFORM nicht auf offscreen setzen"


@pytest.mark.skipif(not _HAS_QT, reason="PySide6 nicht verfuegbar")
def test_generator_guard_rejects_offscreen_even_when_fonts_render(monkeypatch):
    """Offscreen bleibt gesperrt, auch wenn ein Runner echte Glyphen rendert."""
    import generate_store_screenshots as gen

    app = QApplication.instance() or QApplication([])
    assert QApplication.platformName() == "offscreen", (
        "Test erwartet die offscreen-Plattform aus conftest.py"
    )
    monkeypatch.setattr(gen, "font_rendering_works", lambda _app: True)

    with pytest.raises(RuntimeError, match="offscreen"):
        gen._assert_font_rendering(app)


@pytest.mark.skipif(not _HAS_QT, reason="PySide6 nicht verfuegbar")
def test_generator_guard_raises_when_native_font_probe_fails(monkeypatch):
    """Auf nativer Plattform blockiert ein negativer Glyphen-Probe-Befund."""
    import generate_store_screenshots as gen

    class NativeApplication:
        @staticmethod
        def platformName():
            return "xcb"

    monkeypatch.setattr(gen, "QApplication", NativeApplication)
    monkeypatch.setattr(gen, "font_rendering_works", lambda _app: False)

    with pytest.raises(RuntimeError, match="Tofu-Verdacht"):
        gen._assert_font_rendering(object())


def test_build_exe_bat_guarded_preflight():
    """Prueft, ob build_exe.bat die dynamische SOFTWARE_ROOT-Aufloesung und den Scanner-Preflight enthaelt."""
    bat_file = PROJECT_ROOT / "build_exe.bat"
    assert bat_file.exists(), "build_exe.bat fehlt"
    content = bat_file.read_text(encoding="utf-8")
    assert "if exist \"%SCANNER%\"" in content, "Scanner-Guard fehlt in build_exe.bat"
    assert "SOFTWARE_ROOT" in content, "SOFTWARE_ROOT-Variable fehlt in build_exe.bat"
