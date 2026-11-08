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


def test_store_listing_has_tier2_six_languages():
    path = PROJECT_ROOT / "STORE_LISTING.md"
    assert path.exists(), "STORE_LISTING.md fehlt"
    content = path.read_text(encoding="utf-8")
    for lang_header in ["## Deutsch", "## English", "## Español", "## 简体中文", "## 日本語", "## Русский"]:
        assert lang_header in content, f"Sprachabschnitt {lang_header} fehlt in STORE_LISTING.md"


def test_store_package_json_has_six_tier2_languages():
    path = PROJECT_ROOT / "store_package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["languages"] == ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]


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


def test_store_package_json_tier2_descriptions_and_keywords():
    """Prüft, ob alle 6 Tier-2 Sprachen in store_package.json mit Kurzbeschreibung und 7 Keywords vorliegen."""
    path = PROJECT_ROOT / "store_package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for code in ["de", "en", "es", "zh", "ja", "ru"]:
        desc_k = f"description_{code}"
        assert desc_k in data, f"{desc_k} fehlt in store_package.json"
        assert len(data[desc_k]) <= 100, f"{desc_k} > 100 Zeichen ({len(data[desc_k])})"

        kw_k = f"keywords_{code}"
        assert kw_k in data, f"{kw_k} fehlt in store_package.json"
        assert len(data[kw_k]) == 7, f"{kw_k} muss genau 7 Keywords enthalten"
        for kw in data[kw_k]:
            assert len(kw) <= 30, f"Keyword '{kw}' > 30 Zeichen in {kw_k}"


def test_releases_windowsstore_staging_complete():
    """Prüft, ob das Staging-Verzeichnis releases/windowsstore/ vollständig bestückt ist."""
    staging_dir = PROJECT_ROOT / "releases" / "windowsstore"
    assert staging_dir.is_dir(), "releases/windowsstore/ Verzeichnis fehlt"

    expected_files = [
        "BUILD.md",
        "WACK_PROTOCOL.md",
        "store_settings.json",
        "StoreLogo.png",
        "store_listing_de.md",
        "store_listing_en.md",
        "store_listing_es.md",
        "store_listing_zh.md",
        "store_listing_ja.md",
        "store_listing_ru.md",
    ]
    for fname in expected_files:
        fpath = staging_dir / fname
        assert fpath.is_file(), f"Staging-Datei {fname} fehlt in releases/windowsstore/"
        assert fpath.stat().st_size > 10, f"Staging-Datei {fname} ist zu klein"


def test_store_settings_json_has_tier2_six_languages_and_keywords():
    """Prüft store_settings.json im Staging auf Richtlinienkonformität (Policy 10.1.3 & P-006)."""
    settings_file = PROJECT_ROOT / "releases" / "windowsstore" / "store_settings.json"
    assert settings_file.is_file(), "releases/windowsstore/store_settings.json fehlt"
    data = json.loads(settings_file.read_text(encoding="utf-8"))

    assert data.get("identity_name") == "Geiger.CleanMarkdown"
    assert data.get("publisher") == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
    assert data.get("languages") == ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]

    for code in ["de", "en", "es", "zh", "ja", "ru"]:
        dk = f"description_{code}"
        assert dk in data, f"{dk} fehlt in store_settings.json"
        assert len(data[dk]) <= 100, f"{dk} > 100 Zeichen"

        kk = f"keywords_{code}"
        assert kk in data, f"{kk} fehlt in store_settings.json"
        assert len(data[kk]) == 7, f"{kk} muss genau 7 Keywords haben"
        for kw in data[kk]:
            assert len(kw) <= 30, f"Keyword '{kw}' > 30 Zeichen in {kk}"


def test_staging_listings_content_and_keywords():
    """Prüft die 6 lokalisierten Listings im Staging-Ordner."""
    staging_dir = PROJECT_ROOT / "releases" / "windowsstore"
    for code in ["de", "en", "es", "zh", "ja", "ru"]:
        listing_p = staging_dir / f"store_listing_{code}.md"
        assert listing_p.is_file(), f"store_listing_{code}.md fehlt"
        content = listing_p.read_text(encoding="utf-8")
        assert len(content.strip()) > 100, f"store_listing_{code}.md ist zu kurz"
        assert "markdown" in content.lower(), f"store_listing_{code}.md erwähnt markdown nicht"
