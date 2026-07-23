"""Store-Material-Tests für CleanMarkdown.

Prüft, ob alle für den Windows Store benötigten Artefakte vorhanden und
inhaltlich korrekt sind.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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

import re

import pytest

try:
    from PySide6.QtWidgets import QApplication
    _HAS_QT = True
except Exception:  # pragma: no cover - Qt sollte in der Test-Umgebung vorhanden sein
    _HAS_QT = False

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
def test_font_probe_flags_tofu_under_offscreen():
    """Unter offscreen (conftest-Default) muss die Font-Probe Tofu melden."""
    import generate_store_screenshots as gen

    app = QApplication.instance() or QApplication([])
    assert QApplication.platformName() == "offscreen", (
        "Test erwartet die offscreen-Plattform aus conftest.py"
    )
    assert gen.font_rendering_works(app) is False


@pytest.mark.skipif(not _HAS_QT, reason="PySide6 nicht verfuegbar")
def test_generator_guard_raises_on_tofu():
    """Abnahmekriterium: Der Generator wirft, statt still Tofu zu speichern."""
    import generate_store_screenshots as gen

    app = QApplication.instance() or QApplication([])
    with pytest.raises(RuntimeError):
        gen._assert_font_rendering(app)
